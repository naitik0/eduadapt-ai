"""Learner classification: build features from the DB, run the Random Forest, persist the result."""
import sys
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import ROOT_DIR, settings
from ..models import QuizAttempt, RoadmapTopic, StudentTopicProgress, User
from . import roadmap as rm_svc

sys.path.insert(0, str(ROOT_DIR / "ml"))
import predict as ml_predict  # noqa: E402
from features import GOALS, INTERESTS  # noqa: E402


def extract_features(db: Session, user: User) -> dict:
    prof = user.profile
    attempts = list(db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id).order_by(QuizAttempt.created_at)))
    scores = [a.score for a in attempts]
    recent = mean(scores[-3:]) if scores else 0.0
    previous = mean(scores[:-3]) if len(scores) > 3 else recent
    sr = rm_svc.active_student_roadmap(db, user.id)
    prog = []
    if sr:
        prog = list(db.scalars(select(StudentTopicProgress).join(RoadmapTopic, RoadmapTopic.id == StudentTopicProgress.topic_id)
                               .where(StudentTopicProgress.user_id == user.id, RoadmapTopic.roadmap_id == sr.roadmap_id,
                                      RoadmapTopic.is_project.is_(False))))
    started = [p for p in prog if p.started or p.attempts > 0]
    completed = [p for p in started if p.status in ("COMPLETED", "MASTERED")]
    total_q = sum(a.total for a in attempts)
    topic_ids = {a.topic_id for a in attempts if a.topic_id}
    diffs = [t.difficulty for t in db.scalars(select(RoadmapTopic).where(RoadmapTopic.id.in_(topic_ids)))] if topic_ids else []
    topic_mastery = mean(p.mastery for p in prog) if prog else 0.0
    return {
        "previous_score": round(previous, 1),
        "recent_score": round(recent, 1),
        "attempts": len(attempts),
        "study_hours": round(prof.daily_minutes * 7 / 60, 1),
        "completion_rate": round(len(completed) / len(started), 2) if started else 0.5,
        "time_per_question": round(sum(a.time_seconds for a in attempts) / total_q, 1) if total_q else 45.0,
        "topic_mastery": round(topic_mastery, 1),
        "goal": GOALS.index(prof.goal) if prof.goal in GOALS else 4,
        "interest": INTERESTS.index(prof.interests[0]) if prof.interests and prof.interests[0] in INTERESTS else 0,
        "difficulty": round(mean(diffs), 2) if diffs else round(1 + topic_mastery / 40, 2),
    }


def classify(db: Session, user: User) -> dict:
    feats = extract_features(db, user)
    if settings.MODEL_PATH.exists():
        result = ml_predict.predict(feats, settings.MODEL_PATH)
        source = "random_forest"
    else:  # model not trained yet: transparent rule fallback so the app still runs
        lvl = "Beginner" if feats["topic_mastery"] < 35 else "Intermediate" if feats["topic_mastery"] < 65 else "Advanced"
        result = {"learning_level": lvl, "learning_pace": "Moderate", "support_level": "Medium",
                  "confidence": 0.5, "probabilities": {}}
        source = "rules_fallback"
    prof = user.profile
    before = {"learning_level": prof.learning_level, "learning_pace": prof.learning_pace, "support_level": prof.support_level}
    prof.learning_level = result["learning_level"]
    prof.learning_pace = result["learning_pace"]
    prof.support_level = result["support_level"]
    prof.classification_confidence = result["confidence"]
    prof.classification_features = feats
    db.flush()
    return {**result, "features": feats, "source": source, "previous": before}
