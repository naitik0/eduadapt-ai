"""Live feedback loop, run after every important learning event:

  Student action -> Learning event -> Performance update -> Classification update
  -> Mastery / roadmap update -> Recommendation update -> Study plan update

Returns a diff so the UI can show exactly what changed.
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..models import LearningEvent, RoadmapTopic, User
from . import classifier, mastery, recommender, study_plan
from . import roadmap as rm_svc

FULL_LOOP_EVENTS = {"topic_started", "lesson_completed", "practice_completed", "quiz_submitted",
                    "diagnostic_completed", "recommendation_feedback", "profile_updated", "roadmap_initialized"}


def touch_streak(user: User):
    prof, today = user.profile, date.today()
    if prof.last_active_date == today:
        return
    prof.streak_days = prof.streak_days + 1 if prof.last_active_date == today - timedelta(days=1) else 1
    prof.last_active_date = today


def process(db: Session, user: User, event_type: str, topic: RoadmapTopic | None = None,
            payload: dict | None = None, roadmap_id: int | None = None) -> dict:
    payload = payload or {}
    db.add(LearningEvent(user_id=user.id, topic_id=topic.id if topic else None, event_type=event_type, payload=payload))
    touch_streak(user)
    if event_type not in FULL_LOOP_EVENTS:
        db.commit()
        return {"event": event_type, "loop": "logged"}

    roadmap_id = roadmap_id or (topic.roadmap_id if topic else None)
    if roadmap_id is None:
        sr = rm_svc.active_student_roadmap(db, user.id)
        roadmap_id = sr.roadmap_id if sr else None
    if roadmap_id is None:
        db.commit()
        return {"event": event_type, "loop": "no active roadmap"}

    prog = rm_svc.progress_map(db, user.id, roadmap_id)
    before_top = recommender.current(db, user, roadmap_id)[:1] if event_type != "roadmap_initialized" else []
    pipeline, mastery_change = ["learning_event"], None

    # 1. performance / mastery update
    if topic:
        p = prog[topic.id]
        if event_type == "quiz_submitted":
            b, a = mastery.apply_quiz(p, payload["score"], payload.get("difficulty", 1))
        elif event_type == "practice_completed":
            b, a = mastery.apply_practice(p)
        elif event_type == "lesson_completed":
            b, a = mastery.apply_lesson(p)
        elif event_type == "topic_started":
            p.started = True
            b = a = p.mastery
        else:
            b = a = p.mastery
        mastery_change = {"topic_id": topic.id, "topic": topic.title, "before": b, "after": a}
        pipeline.append("performance_update")

    # 2. classification update (Random Forest on fresh features)
    cls = classifier.classify(db, user)
    pipeline.append("classification_update")
    # 3. roadmap update: statuses re-derived from mastery + prerequisites
    changes = rm_svc.sync_statuses(db, user.id, roadmap_id)
    pipeline += ["mastery_update", "roadmap_update"]
    # 4. recommendations
    recs = recommender.recompute(db, user, roadmap_id)
    pipeline.append("recommendation_update")
    # 5. study plan
    study_plan.generate(db, user, roadmap_id)
    pipeline.append("study_plan_update")
    db.commit()

    titles = {t.id: t.title for t in rm_svc.topics_of(db, roadmap_id)}
    unlocked = [titles[t] for t, (old, new) in changes.items() if old == "LOCKED" and new != "LOCKED"]
    new_top = recommender.serialize(db, recs[0]) if recs else None
    return {
        "event": event_type, "pipeline": pipeline, "mastery_change": mastery_change,
        "status_changes": [{"topic_id": t, "topic": titles[t], "from": o, "to": n} for t, (o, n) in changes.items()],
        "unlocked": unlocked,
        "classification": {k: cls[k] for k in ("learning_level", "learning_pace", "support_level", "confidence", "source")},
        "classification_changed": any(cls["previous"][k] != cls[k] for k in cls["previous"]),
        "previous_recommendation": before_top[0]["title"] if before_top else None,
        "recommendation": new_top,
        "recommendation_changed": bool(before_top and new_top and before_top[0]["topic_id"] != new_top["topic_id"]),
    }
