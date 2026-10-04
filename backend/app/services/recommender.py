"""Hybrid recommendation engine: "What should this learner study next?"

Every candidate topic (AVAILABLE / IN_PROGRESS / NEEDS_REVISION) gets seven component
scores in [0, 1], combined with configurable weights (admin-tunable, stored in app_settings).
"""
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..data.roadmaps import GOAL_KEYWORDS, INTEREST_KEYWORDS
from ..models import (AppSetting, QuizAttempt, Recommendation, RecommendationFeedback, RoadmapTopic, User)
from . import roadmap as rm_svc
from .mastery import DIFFICULTY_LABEL, adaptive_difficulty

CANDIDATE_STATUSES = {"AVAILABLE", "IN_PROGRESS", "NEEDS_REVISION"}
PACE_FACTOR = {"Slow": 1.3, "Moderate": 1.0, "Fast": 0.8}
GOAL_LABEL = {"placement": "placement / interview", "job_ready": "job-readiness", "web_development": "web development",
              "data_science": "data science", "fundamentals": "strong-fundamentals", "project_building": "project-building"}


def get_weights(db: Session) -> dict:
    row = db.get(AppSetting, "recommendation_weights")
    w = {**settings.default_weights, **(row.value if row else {})}
    total = sum(w.values()) or 1
    return {k: v / total for k, v in w.items()}          # normalized so scores stay 0-100


def set_weights(db: Session, weights: dict) -> dict:
    clean = {k: max(0.0, float(v)) for k, v in weights.items() if k in settings.default_weights}
    row = db.get(AppSetting, "recommendation_weights")
    if row:
        row.value = clean
    else:
        db.add(AppSetting(key="recommendation_weights", value=clean))
    db.flush()
    return get_weights(db)


def _text(t: RoadmapTopic) -> str:
    return " ".join([t.title, *t.concepts, *t.tags]).lower()


def _keyword_score(text: str, keywords: set[str]) -> int:
    return sum(1 for k in keywords if k in text)


def score_topics(db: Session, user: User, roadmap_id: int) -> list[dict]:
    prof = user.profile
    weights = get_weights(db)
    topics = {t.id: t for t in rm_svc.topics_of(db, roadmap_id)}
    prog = rm_svc.progress_map(db, user.id, roadmap_id)
    pmap = rm_svc.prereq_map(db, roadmap_id)
    deps = rm_svc.dependents_map(pmap)
    candidates = [t for tid, t in topics.items() if prog[tid].status in CANDIDATE_STATUSES]
    if not candidates:   # everything done or locked: offer revision of weakest completed topics
        candidates = sorted([t for tid, t in topics.items() if prog[tid].status == "COMPLETED"],
                            key=lambda t: prog[t.id].mastery)[:5]
    if not candidates:
        return []

    recent_scores = [a.score for a in db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)
                                                 .order_by(QuizAttempt.created_at.desc()).limit(5))]
    recent_avg = mean(recent_scores) if recent_scores else 50.0
    feedback = {}
    for fb in db.scalars(select(RecommendationFeedback).where(RecommendationFeedback.user_id == user.id)):
        feedback[fb.topic_id] = feedback.get(fb.topic_id, 0) + fb.rating
    unlock_counts = {t.id: len([d for d in rm_svc.descendants(t.id, deps)
                                if prog[d].status not in ("COMPLETED", "MASTERED")]) for t in candidates}
    max_unlock = max(unlock_counts.values()) or 1
    max_order = max(t.order for t in topics.values())
    target = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}.get(prof.learning_level, 1)
    target += 0.5 if recent_avg >= 80 else -0.5 if recent_avg < 50 else 0
    goal_kw = GOAL_KEYWORDS.get(prof.goal, set())
    interest_kw = set().union(*[INTEREST_KEYWORDS.get(i, set()) for i in (prof.interests or [])]) if prof.interests else set()

    scored = []
    for t in candidates:
        p = prog[t.id]
        text = _text(t)
        prereq_ms = [prog[pid].mastery for pid, _ in pmap.get(t.id, [])]
        comp = {
            "knowledge_gap": 1 - p.mastery / 100,
            "goal_relevance": min(1.0, 0.3 + 0.25 * _keyword_score(text, goal_kw)
                                  + (0.4 if prof.goal == "project_building" and t.is_project else 0)),
            "prerequisite_priority": 0.7 * unlock_counts[t.id] / max_unlock + 0.3 * (1 - t.order / max_order),
            "recent_performance": (1 - p.last_score / 100) if p.last_score is not None
                                  else (mean(prereq_ms) / 100 if prereq_ms else recent_avg / 100),
            "interest_match": min(1.0, 0.3 + 0.3 * _keyword_score(text, interest_kw)) if interest_kw else 0.5,
            "difficulty_fit": max(0.0, 1 - abs(min(t.difficulty, 3) - target) / 3),
            "feedback": max(0.0, min(1.0, 0.5 + 0.25 * feedback.get(t.id, 0))),
        }
        comp = {k: round(v, 3) for k, v in comp.items()}
        score = round(sum(weights[k] * v for k, v in comp.items()) * 100, 1)
        diff = adaptive_difficulty(prof.learning_level, p.mastery)
        minutes = round(t.est_minutes * PACE_FACTOR.get(prof.learning_pace, 1.0)
                        * (1.1 if prof.support_level == "High" else 1.0) * (1 - p.mastery / 250))
        scored.append({
            "topic_id": t.id, "title": t.title, "level": t.level.name, "status": p.status,
            "mastery": round(p.mastery, 1), "score": score, "components": comp,
            "contributions": {k: round(weights[k] * v * 100, 1) for k, v in comp.items()},
            "difficulty": "Project" if t.is_project else DIFFICULTY_LABEL[diff],
            "est_minutes": max(15, int(5 * round(minutes / 5))),
            "unlocks": unlock_counts[t.id], "prereqs_ok": all(m >= 60 for m in prereq_ms),
            "reason": "",
        })
    scored.sort(key=lambda r: (-r["score"], topics[r["topic_id"]].order))
    for r in scored:
        r["reason"] = explain(r, prof, topics[r["topic_id"]], prog)
    return scored


def explain(r: dict, prof, topic: RoadmapTopic, prog) -> str:
    parts = []
    top = sorted(r["contributions"].items(), key=lambda kv: -kv[1])
    for key, _ in top[:3]:
        c = r["components"][key]
        if key == "knowledge_gap":
            parts.append(f"your {topic.title} mastery is {r['mastery']:.0f}%, so there is a lot to gain"
                         if r["status"] != "NEEDS_REVISION" else
                         f"your last {topic.title} quiz scored {prog[topic.id].last_score:.0f}%, so it needs revision")
        elif key == "goal_relevance" and c >= 0.5:
            parts.append(f"it is directly relevant to your {GOAL_LABEL.get(prof.goal, prof.goal)} goal")
        elif key == "prerequisite_priority" and r["unlocks"]:
            parts.append(f"it unlocks {r['unlocks']} later topic{'s' if r['unlocks'] != 1 else ''}")
        elif key == "interest_match" and c >= 0.6:
            parts.append(f"it matches your interest in {', '.join(prof.interests[:2])}")
        elif key == "difficulty_fit" and c >= 0.66:
            parts.append(f"its difficulty suits your {prof.learning_level.lower()} level")
        elif key == "recent_performance" and c >= 0.6:
            parts.append("your recent results show you're ready for it")
        elif key == "feedback" and c > 0.5:
            parts.append("you rated it helpful before")
    if r["prereqs_ok"] and topic.id and not any("prerequisite" in p for p in parts):
        parts.append("its prerequisites are already sufficiently mastered")
    if not parts:
        parts.append("it is the next step on your roadmap")
    text = ", ".join(parts[:-1]) + (" and " if len(parts) > 1 else "") + parts[-1]
    return text[0].upper() + text[1:] + "."


def recompute(db: Session, user: User, roadmap_id: int, keep: int = 5) -> list[Recommendation]:
    for old in db.scalars(select(Recommendation).where(Recommendation.user_id == user.id,
                                                       Recommendation.is_current.is_(True))):
        old.is_current = False
    rows = []
    for i, r in enumerate(score_topics(db, user, roadmap_id)[:keep]):
        rec = Recommendation(user_id=user.id, roadmap_id=roadmap_id, topic_id=r["topic_id"], rank=i + 1,
                             score=r["score"], components={"components": r["components"],
                                                           "contributions": r["contributions"],
                                                           "unlocks": r["unlocks"], "level": r["level"],
                                                           "status": r["status"], "mastery": r["mastery"]},
                             reason=r["reason"], difficulty=r["difficulty"], est_minutes=r["est_minutes"])
        db.add(rec)
        rows.append(rec)
    db.flush()
    return rows


def serialize(db: Session, rec: Recommendation) -> dict:
    t = db.get(RoadmapTopic, rec.topic_id)
    c = rec.components
    return {"id": rec.id, "rank": rec.rank, "topic_id": rec.topic_id, "title": t.title, "level": c.get("level"),
            "status": c.get("status"), "mastery": c.get("mastery"), "score": rec.score, "reason": rec.reason,
            "difficulty": rec.difficulty, "est_minutes": rec.est_minutes, "components": c.get("components"),
            "contributions": c.get("contributions"), "unlocks": c.get("unlocks"),
            "created_at": rec.created_at.isoformat()}


def current(db: Session, user: User, roadmap_id: int) -> list[dict]:
    recs = list(db.scalars(select(Recommendation).where(Recommendation.user_id == user.id,
                                                        Recommendation.roadmap_id == roadmap_id,
                                                        Recommendation.is_current.is_(True))
                           .order_by(Recommendation.rank)))
    if not recs:
        recs = recompute(db, user, roadmap_id)
        db.commit()
    return [serialize(db, r) for r in recs]
