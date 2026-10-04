import sys

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import ROOT_DIR, settings
from ..database import get_db
from ..deps import admin_user
from ..models import LearningEvent, QuizAttempt, RoadmapTopic, StudentRoadmap, User
from ..services import rag, recommender

sys.path.insert(0, str(ROOT_DIR / "ml"))
import predict as ml_predict  # noqa: E402

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_user)])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    users = list(db.scalars(select(User).order_by(User.id)))
    return {
        "counts": {"users": len(users), "topics": db.scalar(select(func.count(RoadmapTopic.id))),
                   "quiz_attempts": db.scalar(select(func.count(QuizAttempt.id))),
                   "learning_events": db.scalar(select(func.count(LearningEvent.id)))},
        "students": [{"id": u.id, "name": u.name, "email": u.email, "role": u.role,
                      "level": u.profile.learning_level if u.profile else None,
                      "pace": u.profile.learning_pace if u.profile else None,
                      "support": u.profile.support_level if u.profile else None,
                      "roadmaps": db.scalar(select(func.count(StudentRoadmap.id)).where(StudentRoadmap.user_id == u.id))}
                     for u in users],
        "weights": recommender.get_weights(db),
        "model": ml_predict.model_info(settings.MODEL_PATH),
        "rag": rag.stats(), "ai_mode": settings.AI_MODE,
    }


@router.put("/weights")
def update_weights(weights: dict[str, float], db: Session = Depends(get_db)):
    w = recommender.set_weights(db, weights)
    db.commit()
    return w


@router.post("/retrain")
def retrain():
    import train_model  # noqa: E402
    result = train_model.train(model_path=settings.MODEL_PATH)
    ml_predict.reload(settings.MODEL_PATH)
    return result
