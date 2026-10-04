from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import admin, ai, analytics, auth, quiz, recommendations, roadmaps, students, study_plan, topics


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="EduAdapt AI", version="1.0.0", lifespan=lifespan,
              description="Personalised programming education: classification, hybrid recommendation, "
                          "adaptive roadmaps, quizzes, RAG tutor and a live feedback loop.")
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
for r in (auth, students, roadmaps, topics, recommendations, study_plan, quiz, ai, analytics, admin):
    app.include_router(r.router)


@app.get("/health")
def health():
    return {"status": "ok", "ai_mode": settings.AI_MODE}
