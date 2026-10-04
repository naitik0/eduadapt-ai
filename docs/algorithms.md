# Algorithms

## 1. Classification (Random Forest)

**Features** (`ml/features.py`, computed live in `services/classifier.py::extract_features`):

| Feature | Source |
|---|---|
| `previous_score` | Mean of all quiz scores except the last 3 |
| `recent_score` | Mean of the last 3 quiz scores |
| `attempts` | Total quiz attempts |
| `study_hours` | `daily_minutes × days since account creation ÷ 60` (proxy for real time-on-task logs) |
| `completion_rate` | Completed+mastered topics ÷ total topics in the active roadmap |
| `time_per_question` | Mean `time_seconds ÷ total questions` across attempts |
| `topic_mastery` | Mean mastery across all topics touched |
| `goal`, `interest` | Encoded index into `GOALS` / `INTERESTS` |
| `difficulty` | Highest topic difficulty (1–4) reached with mastery ≥ 60 |

**Targets**: `learning_level` (Beginner/Intermediate/Advanced), `learning_pace`
(Slow/Moderate/Fast), `support_level` (Low/Medium/High) — three independent
`RandomForestClassifier` models (`ml/train_model.py`), each reporting accuracy, macro-F1 and
feature importances (visible in the admin panel).

**Synthetic labels** (`ml/generate_dataset.py`, since real learner logs don't exist yet):
```
level_score = 0.40·topic_mastery + 0.25·recent_score + 0.15·previous_score
            + 6·(difficulty−1) + 0.25·min(attempts,40)      → Beginner <38 / Intermediate <66 / Advanced
pace_score  = 45·completion_rate + 1.2·study_hours − 0.35·time_per_question
            + 0.3·(recent−previous) + 10                     → Slow <22 / Moderate <42 / Fast
support_need= 100 − 0.6·recent_score − 25·completion_rate + 0.2·time_per_question
            − 0.2·(recent−previous)                          → High >62 / Medium >38 / Low
```
plus 7% label noise per target. Reported holdout metrics: level accuracy 0.92 / macro-F1 0.91,
pace 0.87 / 0.86, support 0.89 / 0.88 (n=5000, 80/20 split, seed 7 — reproduce with
`python ml/train_model.py`).

**Classification is re-run after every learning event**, not just once at onboarding — see the
feedback loop in `docs/architecture.md`.

## 2. Hybrid recommendation

For every topic with status `AVAILABLE`, `IN_PROGRESS` or `NEEDS_REVISION` (or, if none remain,
the weakest completed topics for revision), `services/recommender.py::score_topics` computes 7
components in `[0, 1]`:

| Component | Formula | Default weight |
|---|---|---|
| `knowledge_gap` | `1 − mastery/100` | 0.30 |
| `goal_relevance` | `min(1, 0.3 + 0.25·keyword_matches(topic_text, goal_keywords))`, +0.4 if the goal is "project_building" and the topic is a project | 0.20 |
| `prerequisite_priority` | `0.7·(topics_this_unlocks / max_unlocks) + 0.3·(1 − order/max_order)` — rewards topics that open up more of the roadmap and come earlier | 0.15 |
| `recent_performance` | `1 − last_score/100` if attempted, else mean prerequisite mastery, else overall recent average | 0.10 |
| `interest_match` | `min(1, 0.3 + 0.3·keyword_matches(topic_text, interest_keywords))` | 0.10 |
| `difficulty_fit` | `1 − |topic_difficulty − target| / 3`, where `target` is the learner's level (1–3) nudged ±0.5 by recent average score | 0.10 |
| `feedback` | `clamp(0.5 + 0.25·net_rating, 0, 1)` from `/recommendations/feedback` | 0.05 |

`score = 100 × Σ(weight × component)`. Weights are stored in `AppSetting` and are
admin-configurable (`PUT /admin/weights`), always renormalised to sum to 1. `explain()` turns the
top 3 contributing components into the human-readable `reason` string shown in the UI — it's
generated from the actual numbers behind that specific recommendation, not a canned sentence.

## 3. Mastery engine

`services/mastery.py`, all mastery values are 0–100 per (student, topic):

- **Quiz**: exponential moving average toward the score — `α=0.7` on the first attempt (recency
  matters most when there's no history), `α=0.55` after — with a +5 bonus for scoring ≥80% on a
  hard quiz, and a −5 "forgetting" penalty for scoring <40% when mastery was already >60.
- **Practice / lesson**: flat +6 / +8, but capped at `COMPLETED_THRESHOLD − 2` (68 by default) —
  studying and practicing can get you close to "complete" but **passing a quiz is required** to
  actually cross the threshold. This is a deliberate design choice, not an oversight.
- **Adaptive difficulty** for quiz delivery: level (1/2/3) shifted +1 if mastery ≥70%, −1 if <25%,
  clamped to [1,3] — so a strong Beginner still sees some Intermediate-difficulty questions.

## 4. Roadmap status & unlocking

`services/roadmap.py::derive_status` — priority order:
1. mastery ≥ `MASTERED_THRESHOLD` (85) → `MASTERED`
2. mastery ≥ `COMPLETED_THRESHOLD` (70) → `COMPLETED`
3. **prerequisites not all ≥ `UNLOCK_THRESHOLD` (60) → `LOCKED`, unconditionally** — this check
   always runs before anything else
4. last quiz <60% and mastery <60% → `NEEDS_REVISION`
5. started or attempted → `IN_PROGRESS`
6. else → `AVAILABLE`

`sync_statuses` recomputes every topic's status from current mastery + the prerequisite graph on
every relevant request, so a topic can never render as unlocked based on stale data.

## 5. Study plan generation

`services/study_plan.py::generate` takes the top recommendations, simulates completing them in
order across a 7-day window at the student's daily-minutes budget, and — because completing a
topic in the simulation can unlock its dependents — pulls in newly-unlocked topics mid-simulation
rather than planning against a static list. Each session is split into `learn` / `examples` /
`practice` / `quiz` blocks using a per-support-level ratio (more supported learners get more
`examples`, less `quiz` weight), with the quiz block only scheduled on the day a topic's minutes
actually run out (a topic that spans two days isn't quizzed until it's actually finished).

## 6. Diagnostic placement

`services/roadmap.py::apply_diagnostic` computes per-level accuracy from the 20 answers, then
**gates** each level's effective accuracy on the level below it having scored ≥60% (so a lucky
guess on 2 hard Advanced questions doesn't place someone past a shaky Beginner foundation).
Effective accuracy is scaled per level (Beginner ×85, Intermediate ×72, Advanced ×60 — steeper
questions naturally cap lower) to set every topic's starting mastery, with a ±15/−20 adjustment
for topics the diagnostic directly tested. Projects always start at 0 mastery regardless of
accuracy — a project is demonstrated, not inferred.

## 7. Retrieval (RAG) for the tutor

`services/rag.py` builds TF-IDF vectors (1–2 grams, ~475 documents: the hand-written knowledge
base plus every topic's own syllabus text) and indexes them with `faiss.IndexFlatIP` (exact inner
product = cosine similarity on L2-normalized vectors). A search re-ranks results with a boost for
matching the current skill/topic before returning the top-k, which is what the tutor cites as
`sources`. This is intentionally simple and dependency-light — no embedding-model download or
GPU required — and isolated behind one function (`rag.search`) so a neural embedding model is a
drop-in replacement if you want one.
