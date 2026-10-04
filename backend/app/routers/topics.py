from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Project, Resource, Roadmap, RoadmapTopic, StudentRoadmap, User
from ..services import feedback_loop, resources
from ..services import roadmap as rm_svc
from ..services.mastery import DIFFICULTY_LABEL, adaptive_difficulty
from .roadmaps import project_out

router = APIRouter(prefix="/topics", tags=["topics"])


def _topic_for_user(db: Session, user: User, topic_id: int) -> RoadmapTopic:
    topic = db.get(RoadmapTopic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    if not db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user.id,
                                                  StudentRoadmap.roadmap_id == topic.roadmap_id)):
        rm_svc.initialize(db, user.id, db.get(Roadmap, topic.roadmap_id).skill.slug)
    return topic


def _require_unlocked(db, user, topic):
    rm_svc.sync_statuses(db, user.id, topic.roadmap_id)
    p = rm_svc.progress_map(db, user.id, topic.roadmap_id)[topic.id]
    if p.status == "LOCKED":
        pmap = rm_svc.prereq_map(db, topic.roadmap_id)
        prog = rm_svc.progress_map(db, user.id, topic.roadmap_id)
        missing = [db.get(RoadmapTopic, pid).title for pid, need in pmap.get(topic.id, []) if prog[pid].mastery < need]
        raise HTTPException(409, f"'{topic.title}' is locked. Reach 60% mastery in: {', '.join(missing)}.")
    return p


@router.get("/{topic_id}")
def topic_detail(topic_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    topic = _topic_for_user(db, user, topic_id)
    rm = db.get(Roadmap, topic.roadmap_id)
    rm_svc.sync_statuses(db, user.id, rm.id)
    prog = rm_svc.progress_map(db, user.id, rm.id)
    pmap = rm_svc.prereq_map(db, rm.id)
    deps = rm_svc.dependents_map(pmap)
    p = prog[topic.id]
    prof = user.profile
    res = list(db.scalars(select(Resource).where(Resource.topic_id == topic.id)))
    practice = next((r for r in res if r.kind == "practice"), None)
    project = db.scalar(select(Project).where(Project.topic_id == topic.id))
    diff = adaptive_difficulty(prof.learning_level, p.mastery)
    db.commit()
    return {
        "id": topic.id, "title": topic.title, "skill": rm.skill.slug, "skill_name": rm.skill.name,
        "level": topic.level.name, "description": topic.description, "objectives": topic.objectives,
        "concepts": topic.concepts, "est_minutes": topic.est_minutes, "is_project": topic.is_project,
        "progress": {"mastery": round(p.mastery, 1), "status": p.status, "attempts": p.attempts,
                     "practice_done": p.practice_done, "last_score": p.last_score, "learned": p.learned},
        "adaptive": {"difficulty": DIFFICULTY_LABEL[diff], "level": prof.learning_level, "support": prof.support_level,
                     "approach": {1: "Simple explanation, simple examples, guided practice, easy quiz",
                                  2: "Deeper explanation, independent practice, medium quiz",
                                  3: "Complex examples, real-world problems, hard quiz, project work"}[diff]},
        "prerequisites": [{"id": pid, "title": db.get(RoadmapTopic, pid).title, "min_mastery": need,
                           "mastery": round(prog[pid].mastery, 1), "met": prog[pid].mastery >= need}
                          for pid, need in pmap.get(topic.id, [])],
        "unlocks": [{"id": d, "title": db.get(RoadmapTopic, d).title} for d in sorted(deps.get(topic.id, []))],
        "resources": resources.rank(res, prof.learning_preference, prof.learning_level, prof.support_level),
        "practice": practice.content.split("\n") if practice else [],
        "project": project_out(project) if project else None,
    }


@router.post("/{topic_id}/start")
def start(topic_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    topic = _topic_for_user(db, user, topic_id)
    _require_unlocked(db, user, topic)
    return feedback_loop.process(db, user, "topic_started", topic)


@router.post("/{topic_id}/complete")
def complete(topic_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Mark the lesson as studied. Completing the topic (70%+) still requires passing its quiz."""
    topic = _topic_for_user(db, user, topic_id)
    _require_unlocked(db, user, topic)
    return feedback_loop.process(db, user, "lesson_completed", topic)


@router.post("/{topic_id}/practice")
def practice_done(topic_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    topic = _topic_for_user(db, user, topic_id)
    _require_unlocked(db, user, topic)
    return feedback_loop.process(db, user, "practice_completed", topic)
