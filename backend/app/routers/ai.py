from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import ChatMessage, ChatSession, Roadmap, RoadmapTopic, User
from ..services import feedback_loop, rag, tutor
from ..services import roadmap as rm_svc

router = APIRouter(prefix="/ai", tags=["ai tutor"])


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    topic_id: int | None = None
    session_id: int | None = None


@router.post("/chat")
def chat(body: ChatIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = db.get(ChatSession, body.session_id) if body.session_id else None
    if session and session.user_id != user.id:
        raise HTTPException(404, "Chat not found")
    topic = db.get(RoadmapTopic, body.topic_id) if body.topic_id else None
    if not session:
        session = ChatSession(user_id=user.id, topic_id=topic.id if topic else None)
        db.add(session)
        db.flush()
    if not topic and session.topic_id:
        topic = db.get(RoadmapTopic, session.topic_id)
    skill = db.get(Roadmap, topic.roadmap_id).skill.slug if topic else None
    if not skill:
        sr = rm_svc.active_student_roadmap(db, user.id)
        skill = db.get(Roadmap, sr.roadmap_id).skill.slug if sr else None
    history = [{"role": m.role, "content": m.content} for m in session.messages]
    result = tutor.answer(db, user, body.message, topic, skill, history)
    db.add(ChatMessage(session_id=session.id, role="user", content=body.message))
    db.add(ChatMessage(session_id=session.id, role="assistant", content=result["answer"], sources=result["sources"]))
    feedback_loop.process(db, user, "tutor_question", topic, {"question": body.message[:200]})
    return {"session_id": session.id, **result}


@router.get("/sessions")
def sessions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    out = []
    for s in db.scalars(select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.id.desc()).limit(20)):
        t = db.get(RoadmapTopic, s.topic_id) if s.topic_id else None
        out.append({"id": s.id, "topic": t.title if t else None, "topic_id": s.topic_id,
                    "created_at": s.created_at.isoformat(), "messages": len(s.messages),
                    "preview": s.messages[0].content[:80] if s.messages else ""})
    return out


@router.get("/sessions/{session_id}")
def session(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = db.get(ChatSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(404, "Chat not found")
    return {"id": s.id, "topic_id": s.topic_id,
            "messages": [{"role": m.role, "content": m.content, "sources": m.sources} for m in s.messages]}


@router.get("/status")
def status():
    live = settings.AI_MODE == "real" and bool(settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY)
    return {"ai_mode": settings.AI_MODE, "live_llm": live, "provider": settings.LLM_PROVIDER if live else None,
            "rag": rag.stats()}
