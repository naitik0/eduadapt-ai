"""AI tutor. The explanation strategy is ours: level, support, weaknesses and retrieved
knowledge decide what the answer contains. The LLM (real mode) only phrases it.

AI_MODE=mock -> deterministic composition from retrieved knowledge (no API key needed)
AI_MODE=real -> Anthropic or OpenAI chat API with the same context; falls back to mock on error
"""
import re

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import QuizAttempt, RoadmapTopic, StudentTopicProgress, User
from . import rag


def build_context(db: Session, user: User, topic: RoadmapTopic | None, skill: str | None) -> dict:
    prof = user.profile
    ctx = {"name": user.name.split()[0], "level": prof.learning_level, "pace": prof.learning_pace,
           "support": prof.support_level, "goal": prof.goal, "skill": skill, "topic": None, "mastery": None,
           "weak_concepts": [], "concepts": [], "preference": prof.learning_preference}
    if topic:
        p = db.scalar(select(StudentTopicProgress).where(StudentTopicProgress.user_id == user.id,
                                                         StudentTopicProgress.topic_id == topic.id))
        last = db.scalar(select(QuizAttempt).where(QuizAttempt.user_id == user.id, QuizAttempt.topic_id == topic.id)
                         .order_by(QuizAttempt.created_at.desc()))
        ctx.update(topic=topic.title, mastery=round(p.mastery) if p else 0, concepts=topic.concepts,
                   weak_concepts=last.weak_concepts if last else [])
    recent = db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)
                        .order_by(QuizAttempt.created_at.desc()).limit(5))
    ctx["recent_weak"] = sorted({c for a in recent for c in a.weak_concepts})[:5]
    return ctx


def _intent(q: str) -> set[str]:
    q = q.lower()
    found = set()
    if re.search(r"example|code|show me|snippet|syntax", q): found.add("example")
    if re.search(r"hint|stuck|help me solve", q): found.add("hint")
    if re.search(r"practice|exercise|quiz me|test me|question", q): found.add("practice")
    if re.search(r"analogy|simple|eli5|like i'm|intuition|real.?world", q): found.add("analogy")
    if re.search(r"mistake|wrong|why did i|feedback|error", q): found.add("feedback")
    return found or {"explain"}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def mock_answer(question: str, ctx: dict, hits: list[dict]) -> str:
    intent = _intent(question)
    lesson = next((h for h in hits if h["kind"] == "lesson"), None)
    syllabus = next((h for h in hits if h["kind"] == "syllabus"), None)
    topic = ctx["topic"] or (lesson or syllabus or {}).get("topic", "this topic")
    level = ctx["level"]
    out = [f"**{topic}**, explained for {'an' if level.lower()[0] in 'aeiou' else 'a'} {level.lower()} learner"
           + (f" (your mastery: {ctx['mastery']}%)" if ctx["mastery"] is not None else "") + "."]

    base = lesson["text"] if lesson else (syllabus["text"] if syllabus else "")
    sents = _sentences(base)
    n = {"Beginner": 2, "Intermediate": 4, "Advanced": 99}[level]
    if ctx["support"] == "High":
        n = max(2, n - 1)
    out.append("### Explanation\n" + " ".join(sents[:n]))
    if level == "Advanced" and len(sents) > n - 1 and ctx["concepts"]:
        out.append("**Going deeper:** connect this to " + ", ".join(ctx["concepts"][-2:])
                   + ". Think about edge cases and performance, not just syntax.")

    analogy = lesson["analogy"] if lesson else ""
    if analogy and ("analogy" in intent or level == "Beginner" or ctx["support"] == "High" or "explain" in intent):
        out.append("### Analogy\n" + analogy)

    code_hit = next((h for h in hits if h["code"]), None)
    if code_hit and ("example" in intent or "explain" in intent or level != "Advanced"):
        out.append(f"### Example\n```{code_hit['lang']}\n{code_hit['code']}\n```")
    elif "example" in intent:
        out.append("### Example\nThere's no stored example for this yet. Try writing the smallest program that uses "
                   + (ctx["concepts"][0] if ctx["concepts"] else topic) + ", run it, then change one thing and predict the result.")

    concepts = ctx["concepts"] or [topic]
    k = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}[level] + (1 if "practice" in intent else 0)
    prompts = {
        "Beginner": "Write a tiny program that uses {c} and print the result. Predict the output before running it.",
        "Intermediate": "Use {c} to solve a small real task (e.g. processing a list of student scores) and explain your choices.",
        "Advanced": "Design a solution where {c} matters for correctness or performance. What breaks at scale, and how would you test it?",
    }
    out.append("### Practice\n" + "\n".join(f"{i + 1}. " + prompts[level].format(c=c) for i, c in enumerate(concepts[:k])))

    if "hint" in intent or ctx["support"] == "High":
        out.append(f"### Hint\nStart from the definition of {concepts[0]}, write the simplest case that works, "
                   "then grow it one step at a time. Print intermediate values to check each step.")

    weak = ctx["weak_concepts"] or ([] if ctx["topic"] else ctx.get("recent_weak", []))
    if weak:
        out.append("### Feedback on your recent mistakes\nIn your last quiz you missed: " + ", ".join(weak[:3])
                   + ". Re-read the explanation above with those in mind, then retry the quiz. Aim for 70%+ to complete the topic.")
    return "\n\n".join(out)


def _system_prompt(ctx: dict, hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits):
        code = ("Code:\n" + h["code"]) if h["code"] else ""
        blocks.append(f"[{i + 1}] {h['source']}\n{h['text']}\n{code}")
    knowledge = "\n\n".join(blocks)
    return (f"You are EduAdapt's programming tutor. Student: level={ctx['level']}, pace={ctx['pace']}, "
            f"support needed={ctx['support']}, goal={ctx['goal']}, current skill={ctx['skill']}, topic={ctx['topic']}, "
            f"mastery={ctx['mastery']}%, recent weak concepts={ctx['weak_concepts'] or ctx.get('recent_weak')}.\n"
            "Adapt depth to the level (Beginner: simple words, one small example; Intermediate: deeper, independent "
            "practice; Advanced: complex examples, trade-offs, real-world problems). Use sections: Explanation, "
            "Analogy, Example (code), Practice, Hint, Feedback on mistakes. Ground answers in the retrieved knowledge "
            "and cite it like [1]. Never give full solutions to practice questions.\n\nRetrieved knowledge:\n" + knowledge)


def real_answer(question: str, ctx: dict, hits: list[dict], history: list[dict]) -> str:
    system = _system_prompt(ctx, hits)
    msgs = [{"role": m["role"], "content": m["content"]} for m in history[-6:]] + [{"role": "user", "content": question}]
    if settings.LLM_PROVIDER == "openai":
        r = httpx.post("https://api.openai.com/v1/chat/completions", timeout=60,
                       headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                       json={"model": settings.LLM_MODEL, "messages": [{"role": "system", "content": system}] + msgs})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    r = httpx.post("https://api.anthropic.com/v1/messages", timeout=60,
                   headers={"x-api-key": settings.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"},
                   json={"model": settings.LLM_MODEL, "max_tokens": 1200, "system": system, "messages": msgs})
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"])


def answer(db: Session, user: User, question: str, topic: RoadmapTopic | None, skill: str | None,
           history: list[dict]) -> dict:
    ctx = build_context(db, user, topic, skill)
    hits = rag.search(question, skill=skill, topic=topic.title if topic else None, k=4)
    mode = "mock"
    if settings.AI_MODE == "real" and (settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY):
        try:
            text, mode = real_answer(question, ctx, hits, history), "real"
        except Exception as e:  # network/auth problems must not break tutoring
            text = mock_answer(question, ctx, hits) + f"\n\n_(Live AI unavailable: {type(e).__name__}. Showing offline answer.)_"
    else:
        text = mock_answer(question, ctx, hits)
    return {"answer": text, "mode": mode, "context": ctx,
            "sources": [{"source": h["source"], "score": h["score"], "kind": h["kind"]} for h in hits]}
