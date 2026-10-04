from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Recommendation, RecommendationFeedback, RoadmapTopic, User
from ..services import feedback_loop, recommender
from ..services import roadmap as rm_svc

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
def list_recs(skill: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sr = rm_svc.active_student_roadmap(db, user.id, skill)
    if not sr:
        raise HTTPException(404, "No roadmap started yet. Pick a skill to begin.")
    return {"weights": recommender.get_weights(db), "recommendations": recommender.current(db, user, sr.roadmap_id)}


class FeedbackIn(BaseModel):
    recommendation_id: int | None = None
    topic_id: int
    rating: int = Field(ge=-1, le=1)
    comment: str = ""


@router.post("/feedback")
def feedback(body: FeedbackIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    topic = db.get(RoadmapTopic, body.topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    if body.recommendation_id and not db.get(Recommendation, body.recommendation_id):
        raise HTTPException(404, "Recommendation not found")
    db.add(RecommendationFeedback(user_id=user.id, recommendation_id=body.recommendation_id, topic_id=topic.id,
                                  rating=body.rating, comment=body.comment))
    db.flush()
    return feedback_loop.process(db, user, "recommendation_feedback", topic, {"rating": body.rating})
