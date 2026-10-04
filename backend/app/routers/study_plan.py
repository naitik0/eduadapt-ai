from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import StudyPlan, StudyPlanItem, User
from ..services import feedback_loop, study_plan
from ..services import roadmap as rm_svc

router = APIRouter(prefix="/study-plan", tags=["study plan"])


def _sr(db, user, skill):
    sr = rm_svc.active_student_roadmap(db, user.id, skill)
    if not sr:
        raise HTTPException(404, "No roadmap started yet. Pick a skill to begin.")
    return sr


@router.get("")
def get_plan(skill: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = _sr(db, user, skill)
    return study_plan.serialize(db, study_plan.current(db, user, sr.roadmap_id))


@router.post("/generate")
def generate(skill: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = _sr(db, user, skill)
    plan = study_plan.generate(db, user, sr.roadmap_id)
    db.commit()
    return study_plan.serialize(db, plan)


class ItemIn(BaseModel):
    done: bool


@router.patch("/items/{item_id}")
def toggle_item(item_id: int, body: ItemIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(StudyPlanItem, item_id)
    if not item or db.get(StudyPlan, item.plan_id).user_id != user.id:
        raise HTTPException(404, "Plan item not found")
    item.done = body.done
    feedback_loop.process(db, user, "plan_item_done" if body.done else "plan_item_undone",
                          payload={"item_id": item_id, "activity": item.activity})
    return {"id": item.id, "done": item.done}
