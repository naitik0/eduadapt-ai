"""Resource generation (at seed time) and personalized matching."""
from urllib.parse import quote_plus

from ..data.knowledge import KNOWLEDGE
from ..models import Resource, RoadmapTopic


def build_for_topic(topic: RoadmapTopic, skill_name: str, skill_slug: str, docs_url: str) -> list[Resource]:
    lesson = next((b for s, t, _, b in KNOWLEDGE if s == skill_slug and t == topic.title), None)
    notes = lesson or (topic.description + "\n\nObjectives:\n" + "\n".join(f"- {o}" for o in topic.objectives))
    q = quote_plus(f"{skill_name} {topic.title} tutorial")
    d, m = topic.difficulty, topic.est_minutes
    practice = "\n".join(
        [f"{i + 1}. " + (f"Write a short {skill_name} snippet that demonstrates {c}." if d == 1 else
                         f"Solve a realistic task using {c}, then refactor it for readability." if d == 2 else
                         f"Build and benchmark a component where {c} is essential; document trade-offs.")
         for i, c in enumerate(topic.concepts[:4])])
    res = [
        Resource(topic_id=topic.id, kind="notes", title=f"{topic.title}: study notes", content=notes,
                 difficulty=d, est_minutes=max(10, m // 3), format="reading"),
        Resource(topic_id=topic.id, kind="video", title=f"Video walkthroughs: {skill_name} {topic.title}",
                 url=f"https://www.youtube.com/results?search_query={q}", difficulty=d,
                 est_minutes=max(10, m // 3), format="visual"),
        Resource(topic_id=topic.id, kind="documentation", title=f"Official {skill_name} documentation",
                 url=docs_url, difficulty=min(3, d + 1), est_minutes=15, format="reading"),
        Resource(topic_id=topic.id, kind="practice", title=f"{topic.title}: practice set", content=practice,
                 difficulty=d, est_minutes=max(15, m // 3), format="hands_on"),
        Resource(topic_id=topic.id, kind="quiz", title=f"{topic.title}: adaptive quiz", url=f"/quiz/{topic.id}",
                 difficulty=d, est_minutes=10, format="hands_on"),
    ]
    if topic.is_project:
        res.append(Resource(topic_id=topic.id, kind="project", title=f"Project brief: {topic.title}",
                            url=f"/topics/{topic.id}", difficulty=4, est_minutes=m, format="hands_on"))
    return res


def rank(resources: list[Resource], preference: str, level: str, support: str) -> list[dict]:
    target = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}.get(level, 1)
    out = []
    for r in resources:
        s = 1.0 - abs(min(r.difficulty, 3) - target) / 3
        why = []
        if r.format == preference:
            s += 0.6
            why.append(f"matches your {preference.replace('_', '-')} preference")
        if support == "High" and r.kind in ("notes", "video"):
            s += 0.3
            why.append("guided material for extra support")
        if level == "Advanced" and r.kind in ("documentation", "practice", "project"):
            s += 0.3
            why.append("depth for an advanced learner")
        if r.kind == "quiz":
            s -= 0.2
        out.append({"id": r.id, "kind": r.kind, "title": r.title, "url": r.url, "content": r.content,
                    "difficulty": r.difficulty, "est_minutes": r.est_minutes, "format": r.format,
                    "match_score": round(s, 2), "why": "; ".join(why) or "fits this topic's difficulty"})
    out.sort(key=lambda x: -x["match_score"])
    return out
