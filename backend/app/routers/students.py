from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..data.roadmaps import GOALS, INTERESTS
from ..database import get_db
from ..deps import current_user
from ..models import Roadmap, StudentRoadmap, User
from ..services import feedback_loop, recommender
from ..services import roadmap as rm_svc

router = APIRouter(prefix="/student", tags=["student"])


class ProfileIn(BaseModel):
    name: str | None = None
    goal: str | None = None
    interests: list[str] | None = None
    daily_minutes: int | None = Field(default=None, ge=15, le=600)
    target_date: date | None = None
    learning_preference: str | None = Field(default=None, pattern="^(reading|visual|hands_on)$")
    onboarded: bool | None = None


def profile_out(user: User) -> dict:
    p = user.profile
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "goal": p.goal,
            "interests": p.interests, "daily_minutes": p.daily_minutes,
            "target_date": p.target_date.isoformat() if p.target_date else None,
            "learning_preference": p.learning_preference, "learning_level": p.learning_level,
            "learning_pace": p.learning_pace, "support_level": p.support_level,
            "classification_confidence": p.classification_confidence,
            "classification_features": p.classification_features, "streak_days": p.streak_days,
            "onboarded": p.onboarded, "options": {"goals": GOALS, "interests": INTERESTS}}


@router.get("/profile")
def get_profile(user: User = Depends(current_user)):
    return profile_out(user)


@router.put("/profile")
def update_profile(body: ProfileIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = user.profile
    if body.goal is not None:
        if body.goal not in GOALS:
            raise HTTPException(422, f"goal must be one of {GOALS}")
        p.goal = body.goal
    if body.interests is not None:
        p.interests = [i for i in body.interests if i in INTERESTS]
    for f in ("daily_minutes", "target_date", "learning_preference", "onboarded"):
        v = getattr(body, f)
        if v is not None:
            setattr(p, f, v)
    if body.name:
        user.name = body.name
    db.flush()
    if rm_svc.active_student_roadmap(db, user.id):
        feedback_loop.process(db, user, "profile_updated")   # goals/time change recommendations + plan
    db.commit()
    return profile_out(user)


class InitIn(BaseModel):
    skill: str


@router.post("/roadmap/initialize")
def initialize(body: InitIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        sr = rm_svc.initialize(db, user.id, body.skill)
    except ValueError as e:
        raise HTTPException(404, str(e))
    db.commit()
    has_history = sr.assessment_done
    if has_history:
        feedback_loop.process(db, user, "roadmap_initialized", roadmap_id=sr.roadmap_id)
    return {"skill": body.skill, "roadmap_id": sr.roadmap_id, "needs_assessment": not has_history,
            "assessment": {"endpoint": f"/quiz?kind=diagnostic&skill={body.skill}", "questions": 20}}


@router.get("/roadmaps")
def my_roadmaps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    out = []
    for sr in db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id)):
        rm = db.get(Roadmap, sr.roadmap_id)
        v = rm_svc.roadmap_view(db, user.id, rm)
        out.append({"skill": rm.skill.slug, "skill_name": rm.skill.name, "is_active": sr.is_active,
                    "assessment_done": sr.assessment_done, "initial_score": sr.initial_score,
                    "completion": v["completion"], "avg_mastery": v["avg_mastery"]})
    db.commit()
    return out


def _resolve(db, user, skill):
    sr = rm_svc.active_student_roadmap(db, user.id, skill)
    if not sr:
        raise HTTPException(404, "No roadmap started yet. Pick a skill to begin.")
    return sr


@router.get("/roadmap")
def my_roadmap(skill: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = _resolve(db, user, skill)
    rm = db.get(Roadmap, sr.roadmap_id)
    view = rm_svc.roadmap_view(db, user.id, rm)
    view["skill_tree"] = rm_svc.skill_tree(db, user.id, rm)
    view["assessment_done"] = sr.assessment_done
    view["is_active"] = sr.is_active
    db.commit()
    return view


@router.get("/roadmap/next-topic")
def next_topic(skill: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = _resolve(db, user, skill)
    recs = recommender.current(db, user, sr.roadmap_id)
    if not recs:
        return {"message": "Every topic is complete. Try a project or start another skill.", "recommendation": None}
    return {"recommendation": recs[0], "alternatives": recs[1:3]}


@router.post("/roadmap/activate")
def activate(body: InitIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = _resolve(db, user, body.skill)
    for other in db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id)):
        other.is_active = other.id == sr.id
    db.commit()
    return feedback_loop.process(db, user, "roadmap_initialized", roadmap_id=sr.roadmap_id) if sr.assessment_done \
        else {"skill": body.skill, "needs_assessment": True}
