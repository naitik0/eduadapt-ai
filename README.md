# EduAdapt AI

Personalised programming education: a diagnostic places you on a technology-specific roadmap,
a Random Forest classifies how you learn, a hybrid recommender picks your next topic, adaptive
quizzes update your mastery, and a live feedback loop keeps the roadmap, recommendations and
study plan in sync after every action. An AI tutor (deterministic mock mode or a real LLM)
answers grounded in a local FAISS knowledge base.

This is a real, runnable full-stack application — FastAPI + SQLAlchemy + scikit-learn on a
SQLite (or Postgres) database, and a React + TypeScript frontend. There is no LLM wrapper doing
the actual work: classification, recommendation, mastery, unlocking and study planning are all
plain Python over real data.

> **Hackathon team project.** EduAdapt AI was built by a team during a hackathon.

## My role: QA Tester (testing & patching)

I was the team's QA tester. I tested the application end to end and patched the issues I found:

- Ran and verified the backend test suite (auth & access control, roadmap graph validity,
  personalisation, feedback loop, AI tutor / ML classifier): **25/25 passing**.
- Verified the frontend production build (TypeScript type-check + Vite build).
- Patched the test configuration to use a JWT secret of the length HS256 requires,
  which removed 52 `InsecureKeyLengthWarning`s from the test run.
- Took generated artifacts (the trained classifier `.joblib`, local virtualenvs, TypeScript build
  info) out of version control. The model is now always retrained by `scripts/setup.sh` / the
  Docker build, so it can't go stale against the installed scikit-learn version.

## Quick start

```bash
git clone https://github.com/naitik0/eduadapt-ai.git && cd eduadapt-ai
./scripts/setup.sh          # installs deps, trains the classifier, seeds the database, npm install
./scripts/run_backend.sh    # FastAPI on :8000  (in one terminal)
./scripts/run_frontend.sh   # Vite dev server on :5173, proxies /api to :8000 (in another)
```

Open http://localhost:5173. Sign in as a demo student (password `demo1234`):

| Email | Level | Skill |
|---|---|---|
| aarav@demo.eduadapt.ai | Beginner | Python |
| meera@demo.eduadapt.ai | Intermediate | Python |
| rohan@demo.eduadapt.ai | Advanced | Java |
| sana@demo.eduadapt.ai | Beginner | C++ |
| kabir@demo.eduadapt.ai | Intermediate | JavaScript |

Admin: `admin@eduadapt.ai` / `admin1234` (recommendation weights, classifier metrics, retrain).

Or `docker compose up --build` and open http://localhost:8080 (the compose file seeds an empty
database automatically on first boot).

## What's real vs. simulated, honestly

- **The classifier is trained on synthetic data** (`ml/generate_dataset.py`, 5,000 rows). Labels
  come from transparent pedagogical rules plus 7% noise, not real learner logs — there weren't
  any to train on. The feature schema (`ml/features.py`) is the real interface; swap in a CSV of
  real learner outcomes with the same 10 columns and retrain, no other code changes needed.
- **The five demo students are real accounts** with a real history: `backend/app/seed.py` runs
  each of them through the actual diagnostic and topic quizzes via the same pipeline a real user
  hits, then backdates the timestamps so the dashboard trend looks lived-in. Nothing about their
  mastery, classification or recommendations is hand-typed.
- **Quiz questions** come from a hand-written bank (`app/data/questions.py`, ~120 questions across
  Python, Java, C++, JavaScript, SQL, DSA, C, Go, Rust and ML) where one exists for the exact
  topic. For the many topics without a hand-written question (most of the 438), the quiz builder
  generates **structural questions** from the roadmap graph itself — "which of these concepts
  belongs to topic X", "what should you know before X", "which topic teaches concept Y", "what
  does mastering X unlock" — using each topic's own `concepts` and prerequisite edges as the
  source of truth. They're synthetic but not arbitrary: getting them right requires actually
  knowing the topic's place in the roadmap.
- **The AI tutor** defaults to `AI_MODE=mock`: a template that assembles a real answer from the
  topic's own description, objectives, concepts, the student's mastery and their recent weak
  concepts, with no model call and no key needed — see it in `app/services/tutor.py`. Set
  `AI_MODE=real` and an `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` to call an actual LLM with the same
  retrieved context; it falls back to mock automatically on any API error.
- **Retrieval (RAG)** uses TF-IDF vectors (1–2 grams) over ~475 documents — the hand-written
  knowledge base (`app/data/knowledge.py`, ~37 worked lessons) plus every topic's own syllabus
  entry — indexed with `faiss.IndexFlatIP`. That's a real, inspectable vector index; it's just
  TF-IDF vectors rather than a neural embedding model, which keeps the whole thing dependency-free
  and reproducible offline. Swapping in a sentence-embedding model is a one-function change in
  `app/services/rag.py`.

## Architecture

```
eduadapt-ai/
├── backend/app/
│   ├── models.py            21 SQLAlchemy tables (users, profiles, roadmaps, topics,
│   │                        prerequisites, progress, quizzes, recommendations, study plans,
│   │                        chat, resources, projects, learning events, admin settings)
│   ├── data/                roadmaps.py (17 skills × beginner→intermediate→advanced→projects,
│   │                        438 topics with prerequisite edges), questions.py (hand-written
│   │                        quiz bank), knowledge.py (tutor/RAG lessons), parser.py
│   ├── services/            roadmap, mastery, classifier, recommender, quiz, study_plan,
│   │                        rag, tutor, resources, feedback_loop, analytics — see docs/algorithms.md
│   ├── routers/              one file per resource, matching docs/api.md
│   └── seed.py               creates the catalog + 5 demo students via the real pipeline
├── ml/                      features.py, generate_dataset.py, train_model.py, predict.py
├── frontend/src/
│   ├── pages/                Landing, Login/Register, Onboarding, Dashboard, Skills, Roadmaps,
│   │                        MyRoadmap (+ per-skill), Topic, Quiz, StudyPlan, Resources, Tutor,
│   │                        Progress, Profile, Admin
│   └── components/           MetroLine (roadmap-as-transit-line), SkillTree (prerequisite graph),
│                            LoopReport (before/after of a feedback-loop run), RecommendationCard,
│                            TutorChat, Charts (Recharts)
├── docs/                    architecture.md, api.md, algorithms.md
├── tests/                   pytest: auth, roadmaps, personalization, feedback loop, AI/ML — 25 tests
└── scripts/                 setup.sh, run_backend.sh, run_frontend.sh, seed.sh, test.sh
```

### The feedback loop

Every meaningful student action (`topic_started`, `lesson_completed`, `practice_completed`,
`quiz_submitted`, `diagnostic_completed`, `profile_updated`, `recommendation_feedback`, …) runs the
same pipeline in `services/feedback_loop.py`:

```
learning event → mastery update → classification (Random Forest) → roadmap statuses
              → recommendations (hybrid re-score) → study plan (regenerated)
```

Every endpoint that triggers it (`/topics/{id}/complete`, `/quiz/submit`, `/student/profile`, …)
returns the full before/after of each stage — which is what `LoopReport` renders in the UI, so
you can see mastery rise, a topic unlock, the classifier shift, and the recommendation change,
all from one action.

### Hybrid recommendation

`services/recommender.py` scores every unlocked topic on 7 weighted signals (defaults: knowledge
gap 0.30, goal relevance 0.20, prerequisite priority 0.15, recent performance 0.10, interest match
0.10, difficulty fit 0.10, your feedback 0.05 — configurable per-deployment via
`RECOMMENDATION_WEIGHTS` or live in the admin panel, normalised to sum to 1). See
`docs/algorithms.md` for the exact formula per component.

## Testing

```bash
./scripts/test.sh     # pytest (25 tests) + frontend production build
```

Tests cover: auth and access control, all 17 roadmaps and their prerequisite graphs being valid
and acyclic, the 5 demo students classifying and recommending differently, diagnostic placement
strength, the feedback loop raising mastery/unlocking topics/changing recommendations and the
study plan, locked-topic enforcement, adaptive quiz difficulty, the mock tutor being grounded and
deterministic, the classifier on synthetic extremes, a second language end-to-end, and admin
weight/retrain controls.

## Configuration

See `.env.example`. Nothing is hardcoded: database URL, JWT secret, AI mode/provider/keys,
mastery thresholds, and recommendation weights are all environment-driven.
