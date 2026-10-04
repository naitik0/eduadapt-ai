"""Roadmap personalization: prerequisite graph, topic status derivation, diagnostic placement."""
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import (Roadmap, RoadmapTopic, Skill, StudentRoadmap, StudentTopicProgress, TopicPrerequisite)

STATUSES = ["LOCKED", "AVAILABLE", "IN_PROGRESS", "COMPLETED", "NEEDS_REVISION", "MASTERED"]
LEVEL_ORDER = ["Beginner", "Intermediate", "Advanced", "Projects"]


def roadmap_by_skill(db: Session, skill_slug: str) -> Roadmap | None:
    return db.scalar(select(Roadmap).join(Skill).where(Skill.slug == skill_slug))


def topics_of(db: Session, roadmap_id: int) -> list[RoadmapTopic]:
    return list(db.scalars(select(RoadmapTopic).where(RoadmapTopic.roadmap_id == roadmap_id).order_by(RoadmapTopic.order)))


def prereq_map(db: Session, roadmap_id: int) -> dict[int, list[tuple[int, float]]]:
    rows = db.execute(select(TopicPrerequisite.topic_id, TopicPrerequisite.prerequisite_id, TopicPrerequisite.min_mastery)
                      .join(RoadmapTopic, RoadmapTopic.id == TopicPrerequisite.topic_id)
                      .where(RoadmapTopic.roadmap_id == roadmap_id)).all()
    out: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for t, p, m in rows:
        out[t].append((p, m))
    return out


def dependents_map(pmap: dict[int, list[tuple[int, float]]]) -> dict[int, set[int]]:
    deps: dict[int, set[int]] = defaultdict(set)
    for t, ps in pmap.items():
        for p, _ in ps:
            deps[p].add(t)
    return deps


def descendants(topic_id: int, deps: dict[int, set[int]]) -> set[int]:
    seen, stack = set(), [topic_id]
    while stack:
        for d in deps.get(stack.pop(), ()):
            if d not in seen:
                seen.add(d)
                stack.append(d)
    return seen


def progress_map(db: Session, user_id: int, roadmap_id: int) -> dict[int, StudentTopicProgress]:
    """Progress rows for every topic in the roadmap (created lazily)."""
    topics = topics_of(db, roadmap_id)
    existing = {p.topic_id: p for p in db.scalars(
        select(StudentTopicProgress).where(StudentTopicProgress.user_id == user_id,
                                           StudentTopicProgress.topic_id.in_([t.id for t in topics])))}
    for t in topics:
        if t.id not in existing:
            p = StudentTopicProgress(user_id=user_id, topic_id=t.id, mastery=0, status="LOCKED")
            db.add(p)
            existing[t.id] = p
    db.flush()
    return existing


def derive_status(p: StudentTopicProgress, unlocked: bool) -> str:
    m = p.mastery
    if m >= settings.MASTERED_THRESHOLD:
        return "MASTERED"
    if m >= settings.COMPLETED_THRESHOLD:
        return "COMPLETED"
    if not unlocked:
        return "LOCKED"                      # prerequisites always win: never unlock early
    if p.attempts > 0 and p.last_score is not None and p.last_score < settings.UNLOCK_THRESHOLD \
            and m < settings.UNLOCK_THRESHOLD:
        return "NEEDS_REVISION"
    if p.started or p.attempts > 0:
        return "IN_PROGRESS"
    return "AVAILABLE"


def sync_statuses(db: Session, user_id: int, roadmap_id: int) -> dict[int, tuple[str, str]]:
    """Recompute every topic status from mastery + prerequisites. Returns {topic_id: (old, new)} changes."""
    pmap = prereq_map(db, roadmap_id)
    prog = progress_map(db, user_id, roadmap_id)
    changes = {}
    for tid, p in prog.items():
        unlocked = all(prog[pid].mastery >= need for pid, need in pmap.get(tid, []))
        new = derive_status(p, unlocked)
        if new != p.status:
            changes[tid] = (p.status, new)
            if new in ("COMPLETED", "MASTERED") and not p.completed_at:
                p.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            p.status = new
    db.flush()
    return changes


def active_student_roadmap(db: Session, user_id: int, skill_slug: str | None = None) -> StudentRoadmap | None:
    q = select(StudentRoadmap).where(StudentRoadmap.user_id == user_id)
    if skill_slug:
        rm = roadmap_by_skill(db, skill_slug)
        if not rm:
            return None
        return db.scalar(q.where(StudentRoadmap.roadmap_id == rm.id))
    return db.scalar(q.where(StudentRoadmap.is_active.is_(True)).order_by(StudentRoadmap.started_at.desc())) \
        or db.scalar(q.order_by(StudentRoadmap.started_at.desc()))


def initialize(db: Session, user_id: int, skill_slug: str) -> StudentRoadmap:
    rm = roadmap_by_skill(db, skill_slug)
    if not rm:
        raise ValueError(f"Unknown skill '{skill_slug}'")
    for sr in db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id == user_id)):
        sr.is_active = False
    sr = db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user_id, StudentRoadmap.roadmap_id == rm.id))
    if not sr:
        sr = StudentRoadmap(user_id=user_id, roadmap_id=rm.id)
        db.add(sr)
    sr.is_active = True
    db.flush()
    sync_statuses(db, user_id, rm.id)
    return sr


def apply_diagnostic(db: Session, user_id: int, roadmap_id: int, results: list[tuple[RoadmapTopic, bool]]) -> dict:
    """Place a student on the roadmap from diagnostic answers.

    Per-level accuracy is gated: a level only counts if the level below it was >= 60%.
    Directly-tested topics get a correctness adjustment. Projects are never pre-credited.
    """
    by_level: dict[str, list[bool]] = defaultdict(list)
    direct: dict[int, list[bool]] = defaultdict(list)
    for topic, ok in results:
        by_level[topic.level.name].append(ok)
        direct[topic.id].append(ok)
    acc = {lvl: (sum(v) / len(v) if v else 0.0) for lvl, v in by_level.items()}
    scale = {"Beginner": 85, "Intermediate": 72, "Advanced": 60, "Projects": 0}
    effective, gate_open = {}, True
    for lvl in LEVEL_ORDER:
        a = acc.get(lvl, 0.0)
        effective[lvl] = a if gate_open else min(a, 0.25)
        gate_open = gate_open and a >= 0.6
    prog = progress_map(db, user_id, roadmap_id)
    for t in topics_of(db, roadmap_id):
        est = effective[t.level.name] * scale[t.level.name]
        if t.id in direct:
            hit = sum(direct[t.id]) / len(direct[t.id])
            est = est + 15 if hit >= 0.5 else est - 20
        prog[t.id].mastery = round(max(0.0, min(95.0, est)), 1)
    overall = sum(ok for _, ok in results) / max(1, len(results)) * 100
    sync_statuses(db, user_id, roadmap_id)
    return {"overall": round(overall, 1), "level_accuracy": {k: round(v * 100, 1) for k, v in acc.items()}}


def roadmap_view(db: Session, user_id: int | None, roadmap: Roadmap) -> dict:
    topics = topics_of(db, roadmap.id)
    pmap = prereq_map(db, roadmap.id)
    prog = progress_map(db, user_id, roadmap.id) if user_id else {}
    by_id = {t.id: t for t in topics}
    levels = []
    for lvl in roadmap.levels:
        items = []
        for t in [x for x in topics if x.level_id == lvl.id]:
            p = prog.get(t.id)
            items.append({
                "id": t.id, "slug": t.slug, "title": t.title, "difficulty": t.difficulty,
                "est_minutes": t.est_minutes, "is_project": t.is_project, "concepts": t.concepts,
                "status": p.status if p else "AVAILABLE", "mastery": round(p.mastery, 1) if p else 0,
                "prerequisites": [{"id": pid, "title": by_id[pid].title, "min_mastery": m} for pid, m in pmap.get(t.id, [])],
            })
        levels.append({"name": lvl.name, "order": lvl.order, "topics": items})
    counts = defaultdict(int)
    for p in prog.values():
        counts[p.status] += 1
    done = counts["COMPLETED"] + counts["MASTERED"]
    return {
        "roadmap_id": roadmap.id, "skill": roadmap.skill.slug, "skill_name": roadmap.skill.name,
        "title": roadmap.title, "description": roadmap.description, "levels": levels,
        "status_counts": dict(counts), "total_topics": len(topics),
        "completion": round(done / len(topics) * 100, 1) if topics and user_id else 0,
        "avg_mastery": round(sum(p.mastery for p in prog.values()) / len(prog), 1) if prog else 0,
    }


def skill_tree(db: Session, user_id: int | None, roadmap: Roadmap) -> dict:
    """Nodes + prerequisite edges, with a depth for layered layout."""
    topics = topics_of(db, roadmap.id)
    pmap = prereq_map(db, roadmap.id)
    prog = progress_map(db, user_id, roadmap.id) if user_id else {}
    depth: dict[int, int] = {}

    def d(tid: int) -> int:
        if tid not in depth:
            depth[tid] = 0 if not pmap.get(tid) else 1 + max(d(p) for p, _ in pmap[tid])
        return depth[tid]

    nodes = [{"id": t.id, "title": t.title, "level": t.level.name, "depth": d(t.id), "is_project": t.is_project,
              "status": prog[t.id].status if prog else "AVAILABLE",
              "mastery": round(prog[t.id].mastery, 1) if prog else 0} for t in topics]
    edges = [{"from": p, "to": t, "min_mastery": m} for t, ps in pmap.items() for p, m in ps]
    return {"skill": roadmap.skill.slug, "nodes": nodes, "edges": edges}
