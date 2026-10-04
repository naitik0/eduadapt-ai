"""Dashboard / progress analytics computed from real database state."""
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (LearningEvent, QuizAttempt, Roadmap, RoadmapTopic, StudentRoadmap, StudentTopicProgress, User)
from . import roadmap as rm_svc


def progress(db: Session, user: User) -> dict:
    sr = rm_svc.active_student_roadmap(db, user.id)
    roadmaps = []
    for s in db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id)):
        rm = db.get(Roadmap, s.roadmap_id)
        view = rm_svc.roadmap_view(db, user.id, rm)
        roadmaps.append({"skill": rm.skill.slug, "skill_name": rm.skill.name, "completion": view["completion"],
                         "avg_mastery": view["avg_mastery"], "is_active": s.is_active,
                         "assessment_done": s.assessment_done, "status_counts": view["status_counts"]})
    topics = []
    if sr:
        by_id = {t.id: t for t in rm_svc.topics_of(db, sr.roadmap_id)}
        prog = rm_svc.progress_map(db, user.id, sr.roadmap_id)
        topics = [{"topic_id": tid, "title": by_id[tid].title, "level": by_id[tid].level.name,
                   "mastery": round(p.mastery, 1), "status": p.status, "attempts": p.attempts,
                   "last_score": p.last_score} for tid, p in sorted(prog.items(), key=lambda kv: by_id[kv[0]].order)]
    return {"active_skill": db.get(Roadmap, sr.roadmap_id).skill.slug if sr else None,
            "roadmaps": roadmaps, "topics": topics}


def analytics(db: Session, user: User) -> dict:
    prof = user.profile
    prog_data = progress(db, user)
    topics = prog_data["topics"]
    attempts = list(db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id).order_by(QuizAttempt.created_at)))
    titles = {t.id: t.title for t in db.scalars(select(RoadmapTopic).where(
        RoadmapTopic.id.in_({a.topic_id for a in attempts if a.topic_id})))} if attempts else {}

    today = date.today()
    trend = []
    done_dates = Counter()
    completed_rows = db.scalars(select(StudentTopicProgress).where(StudentTopicProgress.user_id == user.id,
                                                                   StudentTopicProgress.completed_at.is_not(None)))
    for r in completed_rows:
        done_dates[r.completed_at.date()] += 1
    start = today - timedelta(days=13)
    cum_done = sum(v for d, v in done_dates.items() if d < start)
    events = Counter(e.date() for e in db.scalars(select(LearningEvent.created_at).where(
        LearningEvent.user_id == user.id, LearningEvent.created_at >= datetime.combine(start, datetime.min.time()))))
    by_day = defaultdict(list)
    for a in attempts:
        by_day[a.created_at.date()].append(a.score)
    for i in range(14):
        d = start + timedelta(days=i)
        cum_done += done_dates.get(d, 0)
        trend.append({"date": d.isoformat(), "avg_score": round(mean(by_day[d]), 1) if by_day.get(d) else None,
                      "topics_completed": cum_done, "activity": events.get(d, 0)})

    weak_counter = Counter(c for a in attempts[-10:] for c in a.weak_concepts)
    attempted = [t for t in topics if t["attempts"] > 0 or t["status"] == "NEEDS_REVISION"]
    weak_topics = sorted([t for t in attempted if t["mastery"] < 60], key=lambda t: t["mastery"])[:6]
    level_perf = defaultdict(list)
    for t in topics:
        level_perf[t["level"]].append(t["mastery"])
    done = sum(1 for t in topics if t["status"] in ("COMPLETED", "MASTERED"))
    return {
        "profile": {"name": user.name, "learning_level": prof.learning_level, "learning_pace": prof.learning_pace,
                    "support_level": prof.support_level, "confidence": prof.classification_confidence,
                    "goal": prof.goal, "streak_days": prof.streak_days, "daily_minutes": prof.daily_minutes},
        "active_skill": prog_data["active_skill"],
        "overall_progress": round(done / len(topics) * 100, 1) if topics else 0,
        "avg_mastery": round(mean(t["mastery"] for t in topics), 1) if topics else 0,
        "topics_total": len(topics), "topics_done": done,
        "status_counts": dict(Counter(t["status"] for t in topics)),
        "mastery_by_topic": [t for t in topics if t["mastery"] > 0 or t["status"] != "LOCKED"][:40],
        "level_performance": [{"level": k, "avg_mastery": round(mean(v), 1)} for k, v in level_perf.items()],
        "skill_mastery": [{"skill": r["skill_name"], "avg_mastery": r["avg_mastery"], "completion": r["completion"]}
                          for r in prog_data["roadmaps"]],
        "roadmaps": prog_data["roadmaps"],
        "quiz_performance": [{"id": a.id, "date": a.created_at.isoformat(), "score": a.score, "kind": a.kind,
                              "topic": titles.get(a.topic_id, "Diagnostic")} for a in attempts[-15:]],
        "quiz_avg": round(mean(a.score for a in attempts), 1) if attempts else None,
        "trend": trend,
        "weak_areas": weak_topics,
        "weak_concepts": [{"concept": c, "count": n} for c, n in weak_counter.most_common(6)],
    }
