# Architecture

## Layers

```
React/TS frontend (Vite)          →  Axios  →  FastAPI routers
                                                    │
                                            services/ (pure Python, DB-aware)
                                                    │
                                   SQLAlchemy models  ↔  SQLite/Postgres
                                                    │
                                   ml/ (Random Forest, joblib)
```

- **Routers** (`backend/app/routers/`) do request/response shaping and auth only. They contain no
  business logic — every non-trivial computation lives in `services/` so it's independently
  testable and reusable (the seed script calls the exact same service functions the API does).
- **Services** are plain functions taking a `Session` and returning dicts or ORM rows. None of
  them import FastAPI. This is what let `tests/` exercise the classifier, recommender, RAG index
  and mastery engine directly, without spinning up HTTP.
- **Models** (`backend/app/models.py`) hold 21 tables. SQLite foreign keys are turned on via a
  `PRAGMA` on connect (`database.py`), so cascades and integrity constraints are enforced for real,
  not just declared.
- **ml/** is a standalone package (its own `features.py`) importable both by the backend
  (`services/classifier.py` calls `ml/predict.py`) and from the command line
  (`python ml/predict.py '{"previous_score": 55, ...}'`) or admin's "Retrain" button
  (`POST /admin/retrain` calls `ml/train_model.py` directly and hot-reloads the joblib bundle).

## Request lifecycle for a quiz submission

1. `POST /quiz/submit` (`routers/quiz.py`) grades the quiz (`services/quiz.py::grade`), which is
   pure — no side effects, easy to unit test.
2. It records a `QuizAttempt`, then calls `services/feedback_loop.py::process(event="quiz_submitted")`.
3. The loop runs, in order: `mastery.apply_quiz` → `classifier.classify` → `roadmap.sync_statuses`
   → `recommender.recompute` → `study_plan.generate` — each step reads the DB state the previous
   step just wrote, so there's no separate "sync" job or cron; everything is consistent the
   instant the request returns.
4. The response bundles the before/after of every stage (`LoopResult` in `api/types.ts`), which
   the frontend's `LoopReport` component renders directly — no extra round-trip needed to show
   "what changed."

## Why prerequisites can't be bypassed

`roadmap.derive_status` is the single place a topic's status is computed, and it always checks
`unlocked` (every prerequisite at ≥60% mastery) before anything else — even a 100% mastery topic
renders as `LOCKED` if its prerequisites aren't met (this can't currently happen through normal
use, since mastery on a topic requires visiting it, but the guard is unconditional regardless of
how mastery got set). Every route that starts, completes or quizzes a topic
(`routers/topics.py`, `routers/quiz.py`) calls `roadmap.sync_statuses` and rejects `LOCKED` topics
with `409` before doing anything else — there's no code path that lets you act on a locked topic.

## Frontend structure

- `api/client.ts` — one Axios instance, JWT injected from `localStorage`, 401 → redirect to
  `/login`.
- `api/types.ts` — hand-written TypeScript interfaces mirroring every backend response shape
  exactly (verified against live API output, not guessed).
- `auth/AuthContext.tsx` — the single source of truth for the logged-in profile; every page reads
  it via `useAuth()`.
- `lib/useApi.ts` — a small `GET` hook (loading/error/reload) used by every page instead of
  hand-rolled `useEffect` + `useState` boilerplate.
- `components/MetroLine.tsx` / `SkillTree.tsx` — the roadmap rendered two ways: a linear "metro
  line" per level (the brief's signature visualization) and a force-free, depth-columned
  prerequisite graph you can hover to trace dependencies.
- Design system: "graph-paper notebook" — paper white background with a faint grid, navy ink,
  a highlighter-yellow accent for the current topic, green/crimson for mastered/needs-revision.
  Bricolage Grotesque for headings, Atkinson Hyperlegible for body text (both free, both chosen
  for legibility), JetBrains Mono only for code.

## Deployment

`docker-compose.yml` builds two images: `backend` (Python, trains the model and creates the
SQLite file in a named volume at first boot, self-seeds if the DB is empty) and `frontend`
(multi-stage: `npm run build` then served by nginx, which proxies `/api/*` to the backend
container). For anything beyond a demo, point `DATABASE_URL` at a real Postgres instance — the
code has no SQLite-specific logic beyond the one `PRAGMA` for foreign keys, which is a no-op on
Postgres.
