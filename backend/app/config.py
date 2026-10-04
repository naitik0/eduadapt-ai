"""Central configuration. Everything is overridable via environment variables / .env."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]          # eduadapt-ai/
load_dotenv(ROOT_DIR / ".env")

DEFAULT_WEIGHTS = {
    "knowledge_gap": 0.30,
    "goal_relevance": 0.20,
    "prerequisite_priority": 0.15,
    "recent_performance": 0.10,
    "interest_match": 0.10,
    "difficulty_fit": 0.10,
    "feedback": 0.05,
}


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'data' / 'eduadapt.db'}")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-change-me")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    AI_MODE: str = os.getenv("AI_MODE", "mock").lower()           # mock | real
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")    # anthropic | openai
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    UNLOCK_THRESHOLD: float = float(os.getenv("UNLOCK_THRESHOLD", "60"))
    COMPLETED_THRESHOLD: float = float(os.getenv("COMPLETED_THRESHOLD", "70"))
    MASTERED_THRESHOLD: float = float(os.getenv("MASTERED_THRESHOLD", "85"))
    MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", str(ROOT_DIR / "ml" / "models" / "classifier.joblib")))
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080").split(",")

    @property
    def default_weights(self) -> dict:
        raw = os.getenv("RECOMMENDATION_WEIGHTS")
        if raw:
            try:
                return {**DEFAULT_WEIGHTS, **json.loads(raw)}
            except json.JSONDecodeError:
                pass
        return dict(DEFAULT_WEIGHTS)


settings = Settings()
