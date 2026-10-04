"""Test setup: an isolated temporary SQLite database, seeded once per session through the real seed pipeline."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_tmp = tempfile.mkdtemp(prefix="eduadapt-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["AI_MODE"] = "mock"
os.environ["JWT_SECRET"] = "test-only-secret-at-least-32-bytes-long"  # HS256 wants >= 32 bytes
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import QuizQuestion  # noqa: E402
from app.seed import main as seed  # noqa: E402

DEMO = {
    "aarav": ("aarav@demo.eduadapt.ai", "python", "Beginner"),
    "meera": ("meera@demo.eduadapt.ai", "python", "Intermediate"),
    "rohan": ("rohan@demo.eduadapt.ai", "java", "Advanced"),
    "sana": ("sana@demo.eduadapt.ai", "cpp", "Beginner"),
    "kabir": ("kabir@demo.eduadapt.ai", "javascript", "Intermediate"),
}


@pytest.fixture(scope="session")
def client():
    seed(reset=True)
    with TestClient(app) as c:
        yield c


def login(client, email, password="demo1234"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


_n = [0]


@pytest.fixture
def new_student(client):
    """A freshly registered student with a completed profile."""
    _n[0] += 1
    r = client.post("/auth/register", json={"name": f"Student {_n[0]}", "email": f"s{_n[0]}@test.io",
                                            "password": "password123"})
    assert r.status_code == 201, r.text
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    client.put("/student/profile", headers=h, json={"goal": "placement", "interests": ["data"],
                                                    "daily_minutes": 60, "learning_preference": "hands_on"})
    return h


def answer_key(quiz: dict, correct_first: int | None = None) -> dict:
    """Answers for a served quiz: all correct, or only the first `correct_first` correct."""
    with SessionLocal() as db:
        out = {}
        for i, q in enumerate(quiz["questions"]):
            row = db.get(QuizQuestion, q["id"])
            ok = correct_first is None or i < correct_first
            out[q["id"]] = row.answer_index if ok else (row.answer_index + 1) % len(row.options)
        return out


def take_diagnostic(client, headers, skill, correct_first=None):
    assert client.post("/student/roadmap/initialize", headers=headers, json={"skill": skill}).status_code == 200
    quiz = client.get(f"/quiz?kind=diagnostic&skill={skill}", headers=headers).json()
    r = client.post("/quiz/submit", headers=headers,
                    json={"quiz_id": quiz["quiz_id"], "answers": answer_key(quiz, correct_first), "time_seconds": 600})
    assert r.status_code == 200, r.text
    return quiz, r.json()
