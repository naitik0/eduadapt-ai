"""Quiz engine: adaptive topic quizzes, 20-question diagnostic, grading.

Question sources, in priority order:
  1. hand-written bank (app/data/questions.py), closest difficulty first
  2. structural questions generated from the roadmap graph + concepts (always answerable
     and verifiable from the curriculum itself)
"""
import hashlib
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..data.questions import Q
from ..models import Quiz, QuizQuestion, Roadmap, RoadmapTopic, User
from . import roadmap as rm_svc
from .mastery import adaptive_difficulty

QUESTIONS_BY_DIFFICULTY = {1: 5, 2: 6, 3: 7}
DIAGNOSTIC_SPLIT = {"Beginner": 8, "Intermediate": 7, "Advanced": 5}


def _rng(*parts) -> random.Random:
    return random.Random(int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16))


def bank_for(skill: str, title: str) -> list[dict]:
    return [dict(question=q, options=o, answer_index=a, explanation=e, concept=title, difficulty=d)
            for (t, d, q, o, a, e) in Q.get(skill, []) if t == title]


def structural_questions(topic: RoadmapTopic, all_topics: list[RoadmapTopic], pmap, rng: random.Random) -> list[dict]:
    by_id = {t.id: t for t in all_topics}
    skill_name = topic_skill_name(topic, all_topics)
    others = [t for t in all_topics if t.id != topic.id]
    own = {c.lower() for c in topic.concepts}
    pool = [c for t in others if t.level_id != topic.level_id for c in t.concepts if c.lower() not in own]
    out = []
    for concept in topic.concepts[:3]:
        distract = rng.sample(sorted(set(pool)), k=min(3, len(set(pool))))
        opts = distract + [concept]
        rng.shuffle(opts)
        out.append(dict(question=f"Which of these is a core idea of '{topic.title}' in {skill_name}?",
                        options=opts, answer_index=opts.index(concept),
                        explanation=f"'{topic.title}' covers: {', '.join(topic.concepts)}.",
                        concept=concept, difficulty=topic.difficulty))
    prereqs = [by_id[p] for p, _ in pmap.get(topic.id, [])]
    if prereqs:
        correct = rng.choice(prereqs)
        later = [t for t in others if t.order > topic.order and t.id not in {p.id for p in prereqs}]
        if len(later) >= 3:
            opts = [t.title for t in rng.sample(later, 3)] + [correct.title]
            rng.shuffle(opts)
            out.append(dict(question=f"Which topic should you be comfortable with before starting '{topic.title}'?",
                            options=opts, answer_index=opts.index(correct.title),
                            explanation=f"'{topic.title}' builds on {', '.join(p.title for p in prereqs)}.",
                            concept="prerequisites", difficulty=min(3, topic.difficulty)))
    if len(topic.concepts) >= 3 and pool:            # odd one out
        odd = rng.choice(sorted(set(pool)))
        opts = rng.sample(topic.concepts, 3) + [odd]
        rng.shuffle(opts)
        out.append(dict(question=f"Which of these is NOT part of '{topic.title}' in {skill_name}?",
                        options=opts, answer_index=opts.index(odd),
                        explanation=f"'{odd}' belongs to a different topic; '{topic.title}' covers: {', '.join(topic.concepts)}.",
                        concept="scope of the topic", difficulty=topic.difficulty))
    unlocks = [t for t in others if any(p == topic.id for p, _ in pmap.get(t.id, []))]
    earlier = [t for t in others if t.order < topic.order]
    if unlocks and len(earlier) >= 3:
        nxt = rng.choice(unlocks)
        opts = [t.title for t in rng.sample(earlier, 3)] + [nxt.title]
        rng.shuffle(opts)
        out.append(dict(question=f"Mastering '{topic.title}' directly prepares you for which topic?",
                        options=opts, answer_index=opts.index(nxt.title),
                        explanation=f"'{nxt.title}' lists '{topic.title}' as a prerequisite.",
                        concept="what comes next", difficulty=topic.difficulty))
    if len(others) >= 3:                             # locate a concept on the roadmap
        for concept in topic.concepts[:2]:
            opts = [t.title for t in rng.sample(others, 3)] + [topic.title]
            rng.shuffle(opts)
            out.append(dict(question=f"Which {skill_name} topic teaches '{concept}'?",
                            options=opts, answer_index=opts.index(topic.title),
                            explanation=f"'{concept}' is covered in '{topic.title}'.",
                            concept=concept, difficulty=topic.difficulty))
    for concept in topic.concepts[3:5]:
        levels = ["Beginner", "Intermediate", "Advanced", "Projects"]
        out.append(dict(question=f"In a {skill_name} learning path, '{concept}' is first taught at which stage?",
                        options=levels, answer_index=levels.index(topic.level.name),
                        explanation=f"'{concept}' is part of '{topic.title}' ({topic.level.name}).",
                        concept=concept, difficulty=topic.difficulty))
    return out


def topic_skill_name(topic: RoadmapTopic, all_topics) -> str:
    return topic._skill_name if hasattr(topic, "_skill_name") else "this"


def _attach_skill_names(db: Session, roadmap: Roadmap, topics: list[RoadmapTopic]):
    for t in topics:
        t._skill_name = roadmap.skill.name


def _questions_for_topic(db, roadmap, topic, all_topics, pmap, difficulty, n, rng) -> list[dict]:
    bank = bank_for(roadmap.skill.slug, topic.title)
    bank.sort(key=lambda q: (abs(q["difficulty"] - difficulty), rng.random()))
    picked = bank[:n]
    if len(picked) < n:
        picked += structural_questions(topic, all_topics, pmap, rng)[: n - len(picked)]
    if difficulty >= 2 and len(picked) < n:          # harder quizzes pull in prerequisite questions
        for pid, _ in pmap.get(topic.id, []):
            pt = next(t for t in all_topics if t.id == pid)
            for q in bank_for(roadmap.skill.slug, pt.title):
                if len(picked) < n:
                    picked.append({**q, "concept": f"{pt.title} (prerequisite)"})
    if len(picked) < n:                              # last resort: concept checks on the prerequisites
        seen = {q["question"] + str(q["options"]) for q in picked}
        for pid, _ in pmap.get(topic.id, []):
            pt = next(t for t in all_topics if t.id == pid)
            for q in structural_questions(pt, all_topics, pmap, rng)[:2]:
                if len(picked) < n and q["question"] + str(q["options"]) not in seen:
                    picked.append({**q, "concept": f"{pt.title} (prerequisite)"})
    return picked


def build_topic_quiz(db: Session, user: User, topic: RoadmapTopic) -> Quiz:
    roadmap = db.get(Roadmap, topic.roadmap_id)
    all_topics = rm_svc.topics_of(db, roadmap.id)
    _attach_skill_names(db, roadmap, all_topics)
    pmap = rm_svc.prereq_map(db, roadmap.id)
    prog = rm_svc.progress_map(db, user.id, roadmap.id)
    difficulty = adaptive_difficulty(user.profile.learning_level, prog[topic.id].mastery)
    rng = _rng(user.id, topic.id, prog[topic.id].attempts)
    qs = _questions_for_topic(db, roadmap, topic, all_topics, pmap, difficulty, QUESTIONS_BY_DIFFICULTY[difficulty], rng)
    quiz = Quiz(user_id=user.id, roadmap_id=roadmap.id, topic_id=topic.id, kind="topic", difficulty=difficulty,
                questions=[QuizQuestion(topic_id=topic.id, **q) for q in qs])
    db.add(quiz)
    db.flush()
    return quiz


def build_diagnostic(db: Session, user: User, roadmap: Roadmap) -> Quiz:
    all_topics = [t for t in rm_svc.topics_of(db, roadmap.id) if not t.is_project]
    _attach_skill_names(db, roadmap, all_topics)
    pmap = rm_svc.prereq_map(db, roadmap.id)
    rng = _rng("diag", user.id, roadmap.id)
    questions, used = [], set()

    def take(order, n, per_topic):
        got = 0
        for t in order:
            if got == n:
                break
            qs = bank_for(roadmap.skill.slug, t.title) or structural_questions(t, all_topics, pmap, rng)
            fresh = [q for q in qs if q["question"] not in used]
            have = sum(1 for x in questions if x.topic_id == t.id)
            if fresh and have < per_topic:
                q = rng.choice(fresh)
                used.add(q["question"])
                questions.append(QuizQuestion(topic_id=t.id, **{**q, "concept": t.title}))
                got += 1
        return got

    orders, deficit = {}, 0
    for level, n in DIAGNOSTIC_SPLIT.items():
        lvl_topics = [t for t in all_topics if t.level.name == level]
        banked = [t for t in lvl_topics if bank_for(roadmap.skill.slug, t.title)]
        # spread across the level: prefer topics with hand-written questions, evenly spaced,
        # then the remaining topics; a level with too few topics may ask a second question per topic
        order = []
        for pool in (banked, lvl_topics):
            step = max(1, len(pool) // max(1, n))
            order += [t for t in pool[::step] if t not in order]
        order += [t for t in lvl_topics if t not in order]
        orders[level] = order
        want = n
        got = take(order, want, 1)
        got += take(order, want - got, 2)
        deficit += want - got
    for level in ("Intermediate", "Beginner"):        # tiny roadmaps: top up from the broader levels
        if deficit > 0:
            deficit -= take(orders.get(level, []), deficit, 3)
    quiz = Quiz(user_id=user.id, roadmap_id=roadmap.id, topic_id=None, kind="diagnostic", difficulty=2,
                questions=questions)
    db.add(quiz)
    db.flush()
    return quiz


def public(quiz: Quiz, db: Session) -> dict:
    topic = db.get(RoadmapTopic, quiz.topic_id) if quiz.topic_id else None
    return {"quiz_id": quiz.id, "kind": quiz.kind, "difficulty": quiz.difficulty,
            "difficulty_label": {1: "Easy", 2: "Medium", 3: "Hard"}[quiz.difficulty],
            "topic_id": quiz.topic_id, "topic": topic.title if topic else None,
            "questions": [{"id": q.id, "question": q.question, "options": q.options, "concept": q.concept}
                          for q in quiz.questions]}


def grade(quiz: Quiz, answers: dict[int, int]) -> dict:
    per_q, weak = [], []
    for q in quiz.questions:
        chosen = answers.get(q.id)
        ok = chosen == q.answer_index
        per_q.append({"question_id": q.id, "topic_id": q.topic_id, "correct": ok, "chosen": chosen,
                      "answer_index": q.answer_index, "explanation": q.explanation, "concept": q.concept})
        if not ok and q.concept not in weak:
            weak.append(q.concept)
    correct = sum(r["correct"] for r in per_q)
    total = len(per_q)
    return {"correct": correct, "total": total, "score": round(correct / total * 100, 1) if total else 0,
            "weak_concepts": weak, "results": per_q}
