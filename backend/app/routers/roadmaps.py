from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, Roadmap, RoadmapTopic, Skill
from ..services import roadmap as rm_svc

router = APIRouter(tags=["catalog"])


@router.get("/skills")
def skills(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Roadmap.skill_id, func.count(RoadmapTopic.id))
                             .join(RoadmapTopic, RoadmapTopic.roadmap_id == Roadmap.id).group_by(Roadmap.skill_id)).all())
    return [{"slug": s.slug, "name": s.name, "category": s.category, "description": s.description,
             "topics": counts.get(s.id, 0)} for s in db.scalars(select(Skill).order_by(Skill.id))]


@router.get("/roadmaps")
def roadmaps(db: Session = Depends(get_db)):
    out = []
    for rm in db.scalars(select(Roadmap).order_by(Roadmap.id)):
        topics = rm_svc.topics_of(db, rm.id)
        out.append({"skill": rm.skill.slug, "skill_name": rm.skill.name, "title": rm.title, "category": rm.skill.category,
                    "description": rm.description, "total_topics": len(topics),
                    "levels": [{"name": l.name, "count": sum(1 for t in topics if t.level_id == l.id),
                                "sample": [t.title for t in topics if t.level_id == l.id][:4]} for l in rm.levels]})
    return out


@router.get("/roadmaps/{skill}")
def roadmap(skill: str, db: Session = Depends(get_db)):
    rm = rm_svc.roadmap_by_skill(db, skill)
    if not rm:
        raise HTTPException(404, f"No roadmap for '{skill}'")
    view = rm_svc.roadmap_view(db, None, rm)
    view["skill_tree"] = rm_svc.skill_tree(db, None, rm)
    return view


@router.get("/projects")
def projects(skill: str, db: Session = Depends(get_db)):
    rm = rm_svc.roadmap_by_skill(db, skill)
    if not rm:
        raise HTTPException(404, f"No roadmap for '{skill}'")
    return [project_out(p) for p in db.scalars(select(Project).where(Project.roadmap_id == rm.id).order_by(Project.id))]


def project_out(p: Project) -> dict:
    return {"id": p.id, "topic_id": p.topic_id, "name": p.name, "difficulty": p.difficulty, "est_hours": p.est_hours,
            "required_skills": p.required_skills, "requirements": p.requirements,
            "evaluation_criteria": p.evaluation_criteria,
            "milestones": [{"order": m.order, "title": m.title, "description": m.description} for m in p.milestones]}
