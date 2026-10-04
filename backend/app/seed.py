"""Initialize the database: catalog (skills, roadmaps, topics, prerequisites, projects, resources)
and demo students whose histories are produced by running the REAL pipeline
(diagnostic -> quizzes -> feedback loop), not by typing numbers in.

Usage:  python -m app.seed [--reset]
"""
import argparse
from datetime import date, datetime, timedelta

from sqlalchemy import select

from .data.parser import all_roadmaps
from .data.roadmaps import ROADMAPS
from .database import Base, SessionLocal, engine
from .models import (LearningEvent, Project, ProjectMilestone, QuizAttempt, Roadmap, RoadmapLevel, RoadmapTopic,
                     Skill, StudentProfile, StudentRoadmap, TopicPrerequisite, User)
from .security import hash_password
from .services import feedback_loop, quiz as quiz_svc, resources
from .services import roadmap as rm_svc

DEMO_PASSWORD = "demo1234"


def seed_catalog(db):
    if db.scalar(select(Skill)):
        return False
    for slug, topics in all_roadmaps().items():
        spec = ROADMAPS[slug]
        skill = Skill(slug=slug, name=spec["name"], category=spec["category"], description=spec["description"],
                      docs_url=spec["docs"])
        db.add(skill)
        db.flush()
        rm = Roadmap(skill_id=skill.id, title=f"{spec['name']} Roadmap", description=spec["description"])
        db.add(rm)
        db.flush()
        levels = {}
        for i, name in enumerate(spec["levels"]):
            lvl = RoadmapLevel(roadmap_id=rm.id, name=name, order=i + 1)
            db.add(lvl)
            levels[name] = lvl
        db.flush()
        by_title = {}
        for t in topics:
            tags = [t["level"].lower()] + (["project"] if t["is_project"] else [])
            row = RoadmapTopic(roadmap_id=rm.id, level_id=levels[t["level"]].id, slug=t["slug"], title=t["title"],
                               description=t["description"], concepts=t["concepts"], objectives=t["objectives"],
                               est_minutes=t["est_minutes"], difficulty=t["difficulty"], order=t["order"], tags=tags,
                               is_project=t["is_project"])
            db.add(row)
            by_title[t["title"]] = row
        db.flush()
        project_rank = 0
        for t in topics:
            row = by_title[t["title"]]
            for p in t["prereqs"]:
                db.add(TopicPrerequisite(topic_id=row.id, prerequisite_id=by_title[p].id, min_mastery=60))
            row.level = levels[t["level"]]
            for r in resources.build_for_topic(row, spec["name"], slug, spec["docs"]):
                db.add(r)
            if t["is_project"]:
                project_rank += 1
                n_projects = sum(1 for x in topics if x["is_project"])
                diff = "Beginner" if project_rank <= max(1, n_projects // 3) else \
                    "Intermediate" if project_rank < n_projects else "Advanced"
                proj = Project(roadmap_id=rm.id, topic_id=row.id, name=t["title"], difficulty=diff,
                               est_hours=max(2, t["est_minutes"] // 60), required_skills=t["prereqs"],
                               requirements=[f"Implement {c}" for c in t["concepts"]]
                               + ["Include automated tests for the core logic", "Write a README with setup and usage"],
                               evaluation_criteria=["Correctness: every requirement works on the documented inputs",
                                                    "Code quality: clear structure, naming and error handling",
                                                    "Testing: meaningful automated tests that pass",
                                                    "Documentation: someone else can run it from the README"]
                               + [f"Sound use of {c}" for c in t["concepts"][:2]])
                ms = [("Plan and scaffold", f"Define scope, sketch the design and set up the {spec['name']} project.")]
                ms += [(f"Implement {c}", f"Build and verify the part of the project that handles {c}.") for c in t["concepts"]]
                ms += [("Test and polish", "Add tests, handle edge cases and clean up the code."),
                       ("Document and demo", "Write the README and record a short walkthrough.")]
                proj.milestones = [ProjectMilestone(order=i + 1, title=a, description=b) for i, (a, b) in enumerate(ms)]
                db.add(proj)
    db.commit()
    return True


def _user(db, name, email, password, role="student", **profile):
    u = db.scalar(select(User).where(User.email == email))
    if u:
        return u, False
    u = User(name=name, email=email, password_hash=hash_password(password), role=role)
    u.profile = StudentProfile(**profile)
    db.add(u)
    db.commit()
    return u, True


def _backdate(db, user, days_ago: int, hour: int = 18):
    """Move the most recent attempt + events to a past day so trends and streaks look like real history."""
    when = datetime.combine(date.today() - timedelta(days=days_ago), datetime.min.time()) + timedelta(hours=hour)
    a = db.scalar(select(QuizAttempt).where(QuizAttempt.user_id == user.id).order_by(QuizAttempt.id.desc()))
    if a:
        a.created_at = when
    for e in db.scalars(select(LearningEvent).where(LearningEvent.user_id == user.id,
                                                    LearningEvent.created_at > when)):
        e.created_at = when
    db.commit()


def run_diagnostic(db, user, skill, accuracy: dict, days_ago: int):
    rm = rm_svc.roadmap_by_skill(db, skill)
    rm_svc.initialize(db, user.id, skill)
    quiz = quiz_svc.build_diagnostic(db, user, rm)
    answers, per_level = {}, {}
    for q in quiz.questions:
        lvl = db.get(RoadmapTopic, q.topic_id).level.name
        per_level.setdefault(lvl, []).append(q)
    for lvl, qs in per_level.items():
        k = round(accuracy.get(lvl, 0) * len(qs))
        for i, q in enumerate(qs):
            answers[q.id] = q.answer_index if i < k else (q.answer_index + 1) % len(q.options)
    graded = quiz_svc.grade(quiz, answers)
    db.add(QuizAttempt(user_id=user.id, quiz_id=quiz.id, roadmap_id=rm.id, kind="diagnostic", score=graded["score"],
                       correct=graded["correct"], total=graded["total"], weak_concepts=graded["weak_concepts"],
                       time_seconds=graded["total"] * 40))
    placement = rm_svc.apply_diagnostic(db, user.id, rm.id, [(db.get(RoadmapTopic, r["topic_id"]), r["correct"])
                                                              for r in graded["results"]])
    sr = db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id, StudentRoadmap.roadmap_id == rm.id))
    sr.assessment_done, sr.initial_score = True, placement["overall"]
    user.profile.onboarded = True
    feedback_loop.process(db, user, "diagnostic_completed", payload=placement, roadmap_id=rm.id)
    _backdate(db, user, days_ago)


def take_quiz(db, user, skill, title, target: float, days_ago: int, secs_per_q: int = 35):
    rm = rm_svc.roadmap_by_skill(db, skill)
    topic = db.scalar(select(RoadmapTopic).where(RoadmapTopic.roadmap_id == rm.id, RoadmapTopic.title == title))
    rm_svc.sync_statuses(db, user.id, rm.id)
    if rm_svc.progress_map(db, user.id, rm.id)[topic.id].status == "LOCKED":
        print(f"  ! skipped locked topic {skill}/{title}")
        return
    feedback_loop.process(db, user, "lesson_completed", topic)
    quiz = quiz_svc.build_topic_quiz(db, user, topic)
    k = round(target / 100 * len(quiz.questions))
    answers = {q.id: (q.answer_index if i < k else (q.answer_index + 1) % len(q.options))
               for i, q in enumerate(quiz.questions)}
    graded = quiz_svc.grade(quiz, answers)
    db.add(QuizAttempt(user_id=user.id, quiz_id=quiz.id, roadmap_id=rm.id, topic_id=topic.id, kind="topic",
                       score=graded["score"], correct=graded["correct"], total=graded["total"],
                       weak_concepts=graded["weak_concepts"], time_seconds=graded["total"] * secs_per_q))
    db.flush()
    feedback_loop.process(db, user, "quiz_submitted", topic,
                          {"score": graded["score"], "difficulty": quiz.difficulty,
                           "weak_concepts": graded["weak_concepts"]})
    _backdate(db, user, days_ago)


DEMO_STUDENTS = [
    dict(name="Aarav Sharma", email="aarav@demo.eduadapt.ai", skill="python",
         profile=dict(goal="fundamentals", interests=["automation", "data"], daily_minutes=45,
                      learning_preference="visual", target_date=date.today() + timedelta(days=120)),
         diagnostic={"Beginner": 0.25, "Intermediate": 0.0, "Advanced": 0.0},
         quizzes=[("Python Introduction", 80, 9), ("Installation and Environment", 80, 8), ("Variables", 40, 6),
                  ("Variables", 80, 5), ("Data Types", 60, 3), ("Data Types", 80, 2), ("Input/Output", 60, 1)], streak=4, secs=55),
    dict(name="Meera Iyer", email="meera@demo.eduadapt.ai", skill="python",
         profile=dict(goal="job_ready", interests=["web", "data"], daily_minutes=90,
                      learning_preference="hands_on", target_date=date.today() + timedelta(days=75)),
         diagnostic={"Beginner": 1.0, "Intermediate": 0.72, "Advanced": 0.2},
         quizzes=[("Modules", 83, 10), ("OOP", 50, 8), ("OOP", 83, 6), ("Classes", 67, 4), ("Git/GitHub", 100, 3),
                  ("Packages", 83, 3), ("Virtual Environments", 83, 2), ("Classes", 83, 1)], streak=6, secs=35),
    dict(name="Rohan Verma", email="rohan@demo.eduadapt.ai", skill="java",
         profile=dict(goal="job_ready", interests=["cloud", "systems"], daily_minutes=120,
                      learning_preference="reading", target_date=date.today() + timedelta(days=60)),
         diagnostic={"Beginner": 1.0, "Intermediate": 1.0, "Advanced": 0.6},
         quizzes=[("Multithreading", 86, 9), ("JVM Internals", 86, 7), ("Build Tools", 100, 6),
                  ("Spring Boot", 71, 4), ("Concurrency Utilities", 86, 2), ("REST APIs with Spring", 71, 1)],
         streak=9, secs=22),
    dict(name="Sana Khan", email="sana@demo.eduadapt.ai", skill="cpp",
         profile=dict(goal="placement", interests=["games", "systems"], daily_minutes=60,
                      learning_preference="visual", target_date=date.today() + timedelta(days=150)),
         diagnostic={"Beginner": 0.38, "Intermediate": 0.0, "Advanced": 0.0},
         quizzes=[("C++ Basics", 60, 7), ("C++ Basics", 80, 5), ("Variables and Types", 40, 3)], streak=2, secs=60),
    dict(name="Kabir Mehta", email="kabir@demo.eduadapt.ai", skill="javascript",
         profile=dict(goal="web_development", interests=["web"], daily_minutes=75,
                      learning_preference="hands_on", target_date=date.today() + timedelta(days=90)),
         diagnostic={"Beginner": 0.88, "Intermediate": 0.57, "Advanced": 0.2},
         quizzes=[("ES6+ Features", 83, 8), ("Functions", 83, 7), ("Scope and Hoisting", 83, 6), ("Closures", 33, 3),
                  ("Error Handling", 83, 2)], streak=3, secs=38),
]


def seed_users(db):
    _user(db, "EduAdapt Admin", "admin@eduadapt.ai", "admin1234", role="admin", onboarded=True)
    for s in DEMO_STUDENTS:
        u, created = _user(db, s["name"], s["email"], DEMO_PASSWORD, **s["profile"])
        if not created:
            continue
        run_diagnostic(db, u, s["skill"], s["diagnostic"], days_ago=12)
        for title, score, days_ago in s["quizzes"]:
            take_quiz(db, u, s["skill"], title, score, days_ago, s["secs"])
        u.profile.streak_days = s["streak"]
        u.profile.last_active_date = date.today() - timedelta(days=1)
        db.commit()


def main(reset: bool = False):
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        created = seed_catalog(db)
        seed_users(db)
        n_topics = len(list(db.scalars(select(RoadmapTopic.id))))
    print(f"catalog {'created' if created else 'already present'}: {n_topics} topics; demo users ready "
          f"(password '{DEMO_PASSWORD}', admin: admin@eduadapt.ai / admin1234)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="drop and recreate all tables")
    main(ap.parse_args().reset)
