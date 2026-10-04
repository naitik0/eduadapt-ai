# API reference

Base URL: `http://localhost:8000` (or `/api` behind the Vite proxy / nginx). All routes except
`/auth/*`, `/health`, `/skills`, `/roadmaps*` and `/projects` require `Authorization: Bearer <token>`.
Interactive docs are also live at `/docs` (Swagger) and `/redoc` whenever the backend is running.

## Auth
| Method | Path | Notes |
|---|---|---|
| POST | `/auth/register` | `{name, email, password}` → token + user |
| POST | `/auth/login` | `{email, password}` → token + user |

## Student profile & roadmap
| Method | Path | Notes |
|---|---|---|
| GET | `/student/profile` | Full profile incl. classification + confidence + raw features |
| PUT | `/student/profile` | Update goal/interests/daily_minutes/target_date/learning_preference; re-runs the feedback loop if a roadmap is active |
| GET | `/skills` | All 17 skills with topic counts |
| GET | `/roadmaps` | Summary of every roadmap (levels + sample topics) |
| GET | `/roadmaps/{skill}` | Full topic tree for one skill (no auth; no personal progress) |
| POST | `/student/roadmap/initialize` | `{skill}` → creates the roadmap enrollment; `needs_assessment` tells the frontend whether to route to the diagnostic |
| GET | `/student/roadmaps` | This student's roadmaps + completion, for the multi-skill switcher |
| GET | `/student/roadmap?skill=` | Full personalised view: every topic's status/mastery + `skill_tree` (nodes/edges) |
| GET | `/student/roadmap/next-topic?skill=` | Top recommendation + 2 alternatives |
| POST | `/student/roadmap/activate` | `{skill}` → makes that roadmap the active one (drives the dashboard) |

## Topics
| Method | Path | Notes |
|---|---|---|
| GET | `/topics/{id}` | Full detail: progress, adaptive difficulty, prerequisites/unlocks, ranked resources, project brief |
| POST | `/topics/{id}/start` | 409 if locked. Runs the feedback loop. |
| POST | `/topics/{id}/complete` | Marks the lesson studied (+mastery, capped below 70%). Runs the feedback loop. |
| POST | `/topics/{id}/practice` | Logs a completed practice set (+mastery, same cap). Runs the feedback loop. |
| GET | `/projects?skill=` | Every project in a roadmap with milestones + evaluation criteria |

## Quiz
| Method | Path | Notes |
|---|---|---|
| GET | `/quiz?kind=diagnostic&skill=` | 20-question diagnostic across all levels |
| GET | `/quiz?topic_id=` | Adaptive topic quiz (5/6/7 questions by difficulty) |
| POST | `/quiz/submit` | `{quiz_id, answers: {question_id: option_index}, time_seconds}` → score + explanations + full `loop` result. A diagnostic submit also returns `placement`. Re-submitting the same `quiz_id` is `409`. |

## Recommendations & study plan
| Method | Path | Notes |
|---|---|---|
| GET | `/recommendations?skill=` | Current weights + top 5 recommendations with score breakdown |
| POST | `/recommendations/feedback` | `{recommendation_id?, topic_id, rating: -1\|1, comment?}` → nudges future scoring, runs the loop |
| GET | `/study-plan?skill=` | Current plan (today + 7-day week) |
| POST | `/study-plan/generate?skill=` | Force a fresh plan from current recommendations |
| PATCH | `/study-plan/items/{id}` | `{done}` → toggle a checklist item |

## AI tutor
| Method | Path | Notes |
|---|---|---|
| POST | `/ai/chat` | `{message, topic_id?, session_id?}` → grounded answer + RAG sources. Mock mode is deterministic per (topic, message, mastery). |
| GET | `/ai/sessions` | Last 20 chat sessions with previews |
| GET | `/ai/sessions/{id}` | Full message history |
| GET | `/ai/status` | `{ai_mode, live_llm, provider, rag: {documents, dimensions, index}}` |

## Analytics
| Method | Path | Notes |
|---|---|---|
| GET | `/progress` | Compact per-topic mastery + per-skill completion |
| GET | `/analytics` | Everything the dashboard needs: trend, quiz history, skill/level mastery, weak areas/concepts |

## Admin (role=admin)
| Method | Path | Notes |
|---|---|---|
| GET | `/admin/overview` | User counts, every student's classification, current weights, model metrics, RAG stats |
| PUT | `/admin/weights` | Set the 7 recommendation weights (any positive values; normalised to sum to 1) |
| POST | `/admin/retrain` | Retrains the Random Forest on `data/synthetic_learners.csv` and hot-reloads it |

## Errors

Standard FastAPI/Pydantic shape: `{"detail": "message"}` for a single error, or a list of
`{"loc", "msg", "type"}` for validation errors. The frontend's `errorMessage()` helper
(`src/api/client.ts`) handles both.
