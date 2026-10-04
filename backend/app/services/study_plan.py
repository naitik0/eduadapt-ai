"""Daily + weekly study plans generated from recommendations, pace, support level and time budget."""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import RoadmapTopic, StudyPlan, StudyPlanItem, User
from . import recommender
from . import roadmap as rm_svc

SPLITS = {   # share of a topic session per activity, by support level
    "Low": [("learn", .35), ("examples", .15), ("practice", .30), ("quiz", .20)],
    "Medium": [("learn", .35), ("examples", .25), ("practice", .25), ("quiz", .15)],
    "High": [("learn", .30), ("examples", .30), ("practice", .25), ("quiz", .15)],
}
DAYS = 7


def _blocks(topic: RoadmapTopic, minutes: int, support: str, status: str, final: bool = True) -> list[tuple[str, int]]:
    if topic.is_project:
        return [("project", minutes)]
    split = SPLITS.get(support, SPLITS["Medium"])
    if not final:                               # topic continues tomorrow: quiz comes at the end, not now
        split = [(a, sh / (1 - split[-1][1])) for a, sh in split[:-1]]
    out = [("review", 10)] if status == "NEEDS_REVISION" and minutes > 25 else []
    rest = minutes - sum(m for _, m in out)
    if rest < 30:                               # a short slot: continue the topic rather than split it thinly
        return out + ([("practice", rest - 10), ("quiz", 10)] if rest >= 20 and final
                     else [("practice" if final else "learn", rest)])
    raw = [[a, max(5, int(5 * round(rest * share / 5)))] for a, share in split]
    raw[-2 if final else -1][1] += rest - sum(m for _, m in raw)  # keep the blocks summing exactly to the slot
    return out + [tuple(x) for x in raw]


def generate(db: Session, user: User, roadmap_id: int) -> StudyPlan:
    prof = user.profile
    daily = max(15, prof.daily_minutes)
    recs = recommender.score_topics(db, user, roadmap_id)
    topics = {t.id: t for t in rm_svc.topics_of(db, roadmap_id)}
    prog = rm_svc.progress_map(db, user.id, roadmap_id)
    pmap = rm_svc.prereq_map(db, roadmap_id)

    # Simulate the week: assume each scheduled topic gets completed, which may unlock others.
    simulated = {tid: p.mastery for tid, p in prog.items()}
    queue = [(r["topic_id"], r["est_minutes"], r["status"]) for r in recs]
    queued = {q[0] for q in queue}
    items, day, used, order = [], 0, 0, 0
    while queue and day < DAYS:
        tid, minutes, status = queue.pop(0)
        remaining = minutes
        while remaining > 0 and day < DAYS:
            room = daily - used
            if room < 10:
                day, used, order = day + 1, 0, 0
                continue
            chunk = min(room, remaining)
            for activity, m in _blocks(topics[tid], chunk, prof.support_level, status, final=chunk >= remaining):
                items.append(StudyPlanItem(topic_id=tid, day=day, order=order, activity=activity, minutes=m))
                order += 1
            used += chunk
            remaining -= chunk
        simulated[tid] = max(simulated[tid], settings.COMPLETED_THRESHOLD)
        for cand in sorted(topics.values(), key=lambda t: t.order):  # newly unlocked by the simulation
            if cand.id in queued or simulated[cand.id] >= settings.COMPLETED_THRESHOLD:
                continue
            if all(simulated[p] >= need for p, need in pmap.get(cand.id, [])):
                queue.append((cand.id, cand.est_minutes, "AVAILABLE"))
                queued.add(cand.id)
                break

    remaining_minutes = sum(t.est_minutes * (1 - prog[t.id].mastery / 100) for t in topics.values()
                            if prog[t.id].status not in ("COMPLETED", "MASTERED"))
    pace = recommender.PACE_FACTOR.get(prof.learning_pace, 1.0)
    days_needed = int(remaining_minutes * pace / daily) + 1
    summary = {"remaining_minutes": int(remaining_minutes * pace), "days_to_complete": days_needed,
               "estimated_completion": (date.today() + timedelta(days=days_needed)).isoformat(),
               "topics_scheduled": len({i.topic_id for i in items})}
    if prof.target_date:
        days_left = max(1, (prof.target_date - date.today()).days)
        summary.update({"target_date": prof.target_date.isoformat(), "on_track": days_needed <= days_left,
                        "minutes_per_day_needed": int(remaining_minutes * pace / days_left) + 1})

    old_done = {}
    for old in db.scalars(select(StudyPlan).where(StudyPlan.user_id == user.id, StudyPlan.is_current.is_(True))):
        if old.start_date == date.today():
            old_done.update({(i.topic_id, i.activity, i.day): True for i in old.items if i.done})
        old.is_current = False
    plan = StudyPlan(user_id=user.id, roadmap_id=roadmap_id, start_date=date.today(), daily_minutes=daily,
                     summary=summary, items=items)
    for it in items:
        it.done = old_done.get((it.topic_id, it.activity, it.day), False)
    db.add(plan)
    db.flush()
    return plan


def current(db: Session, user: User, roadmap_id: int) -> StudyPlan:
    plan = db.scalar(select(StudyPlan).where(StudyPlan.user_id == user.id, StudyPlan.roadmap_id == roadmap_id,
                                             StudyPlan.is_current.is_(True)).order_by(StudyPlan.id.desc()))
    if not plan or plan.start_date != date.today():
        plan = generate(db, user, roadmap_id)
        db.commit()
    return plan


def serialize(db: Session, plan: StudyPlan) -> dict:
    titles = {t.id: t.title for t in rm_svc.topics_of(db, plan.roadmap_id)}
    days = []
    for d in range(DAYS):
        its = [i for i in plan.items if i.day == d]
        days.append({"day": d, "date": (plan.start_date + timedelta(days=d)).isoformat(),
                     "total_minutes": sum(i.minutes for i in its),
                     "items": [{"id": i.id, "topic_id": i.topic_id, "topic": titles.get(i.topic_id, "?"),
                                "activity": i.activity, "minutes": i.minutes, "done": i.done} for i in its]})
    return {"id": plan.id, "start_date": plan.start_date.isoformat(), "daily_minutes": plan.daily_minutes,
            "summary": plan.summary, "today": days[0], "week": days, "created_at": plan.created_at.isoformat()}
