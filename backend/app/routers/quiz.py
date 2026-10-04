from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Quiz, QuizAttempt, Roadmap, RoadmapTopic, StudentRoadmap, User
from ..services import feedback_loop, quiz as quiz_svc
from ..services import roadmap as rm_svc
from sqlalchemy import select

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("")
def get_quiz(topic_id: int | None = None, kind: str = "topic", skill: str | None = None,
             user: User = Depends(current_user), db: Session = Depends(get_db)):
    if kind == "diagnostic":
        rm = rm_svc.roadmap_by_skill(db, skill) if skill else None
        if not rm:
            sr = rm_svc.active_student_roadmap(db, user.id)
            rm = db.get(Roadmap, sr.roadmap_id) if sr else None
        if not rm:
            raise HTTPException(404, "Choose a skill for the diagnostic assessment")
        rm_svc.initialize(db, user.id, rm.skill.slug)
        quiz = quiz_svc.build_diagnostic(db, user, rm)
    else:
        topic = db.get(RoadmapTopic, topic_id) if topic_id else None
        if not topic:
            raise HTTPException(404, "Topic not found")
        if not db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id,
                                                      StudentRoadmap.roadmap_id == topic.roadmap_id)):
            rm_svc.initialize(db, user.id, db.get(Roadmap, topic.roadmap_id).skill.slug)
        rm_svc.sync_statuses(db, user.id, topic.roadmap_id)
        if rm_svc.progress_map(db, user.id, topic.roadmap_id)[topic.id].status == "LOCKED":
            raise HTTPException(409, f"'{topic.title}' is locked until its prerequisites reach 60% mastery.")
        quiz = quiz_svc.build_topic_quiz(db, user, topic)
    db.commit()
    return quiz_svc.public(quiz, db)


class SubmitIn(BaseModel):
    quiz_id: int
    answers: dict[int, int]
    time_seconds: int = Field(default=0, ge=0)


@router.post("/submit")
def submit(body: SubmitIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quiz = db.get(Quiz, body.quiz_id)
    if not quiz or quiz.user_id != user.id:
        raise HTTPException(404, "Quiz not found")
    if db.scalar(select(QuizAttempt).where(QuizAttempt.quiz_id == quiz.id)):
        raise HTTPException(409, "This quiz was already submitted. Start a new attempt.")
    graded = quiz_svc.grade(quiz, body.answers)
    db.add(QuizAttempt(user_id=user.id, quiz_id=quiz.id, roadmap_id=quiz.roadmap_id, topic_id=quiz.topic_id,
                       kind=quiz.kind, score=graded["score"], correct=graded["correct"], total=graded["total"],
                       weak_concepts=graded["weak_concepts"], time_seconds=body.time_seconds))
    db.flush()
    if quiz.kind == "diagnostic":
        results = [(db.get(RoadmapTopic, r["topic_id"]), r["correct"]) for r in graded["results"]]
        placement = rm_svc.apply_diagnostic(db, user.id, quiz.roadmap_id, results)
        sr = db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id,
                                                    StudentRoadmap.roadmap_id == quiz.roadmap_id))
        sr.assessment_done, sr.initial_score = True, placement["overall"]
        user.profile.onboarded = True
        db.flush()
        loop = feedback_loop.process(db, user, "diagnostic_completed", payload=placement, roadmap_id=quiz.roadmap_id)
        return {**graded, "placement": placement, "loop": loop}
    topic = db.get(RoadmapTopic, quiz.topic_id)
    loop = feedback_loop.process(db, user, "quiz_submitted", topic,
                                 {"score": graded["score"], "difficulty": quiz.difficulty,
                                  "weak_concepts": graded["weak_concepts"]})
    return {**graded, "loop": loop}
