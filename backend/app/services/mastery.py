"""Mastery / performance engine. Mastery is 0-100 per topic.

quiz:      exponential moving average toward the quiz score; first attempt weighs more,
           hard quizzes passed well earn a small bonus
practice:  +6 per completed practice set, capped below COMPLETED (a quiz is required to complete)
lesson:    +8 once when a lesson is marked learned, same cap
"""
from datetime import datetime, timezone

from ..config import settings
from ..models import StudentTopicProgress

PRE_QUIZ_CAP = settings.COMPLETED_THRESHOLD - 2   # practice/lessons alone can't complete a topic


def _clamp(x: float) -> float:
    return round(max(0.0, min(100.0, x)), 1)


def apply_quiz(p: StudentTopicProgress, score: float, difficulty: int) -> tuple[float, float]:
    before = p.mastery
    alpha = 0.7 if p.attempts == 0 else 0.55
    new = before * (1 - alpha) + score * alpha
    if difficulty >= 3 and score >= 80:
        new += 5
    if score < 40 and before > 60:           # a poor result on a known topic signals forgetting
        new -= 5
    p.mastery = _clamp(new)
    p.attempts += 1
    p.last_score = score
    p.started = True
    p.started_at = p.started_at or datetime.now(timezone.utc).replace(tzinfo=None)
    return before, p.mastery


def apply_practice(p: StudentTopicProgress) -> tuple[float, float]:
    before = p.mastery
    p.practice_done += 1
    p.started = True
    p.started_at = p.started_at or datetime.now(timezone.utc).replace(tzinfo=None)
    if before < PRE_QUIZ_CAP:
        p.mastery = _clamp(min(PRE_QUIZ_CAP, before + 6))
    return before, p.mastery


def apply_lesson(p: StudentTopicProgress) -> tuple[float, float]:
    before = p.mastery
    p.started = True
    p.started_at = p.started_at or datetime.now(timezone.utc).replace(tzinfo=None)
    if not p.learned:
        p.learned = True
        if before < PRE_QUIZ_CAP:
            p.mastery = _clamp(min(PRE_QUIZ_CAP, before + 8))
    return before, p.mastery


def adaptive_difficulty(level: str, mastery: float) -> int:
    """1=Beginner, 2=Intermediate, 3=Advanced delivery for a topic, from classification + mastery."""
    idx = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}.get(level, 1)
    if mastery >= 70:
        idx += 1
    elif mastery < 25:
        idx -= 1
    return max(1, min(3, idx))


DIFFICULTY_LABEL = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}
