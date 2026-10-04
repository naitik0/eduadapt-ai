import { CheckCircle2, Clock, XCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { Quiz, QuizResult } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import LoopReport from "../components/LoopReport";
import { Card, ErrorState, Loading, PageHeader, Pill } from "../components/ui";

export default function QuizPage() {
  const { skill, topicId } = useParams();
  const diagnostic = !!skill;
  const nav = useNavigate();
  const { refresh } = useAuth();
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const started = useRef(Date.now());
  const fetched = useRef<string | null>(null);

  const url = diagnostic ? `/quiz?kind=diagnostic&skill=${skill}` : `/quiz?topic_id=${topicId}`;

  async function load() {
    setError(null);
    setQuiz(null);
    setResult(null);
    setAnswers({});
    try {
      const { data } = await api.get<Quiz>(url);
      setQuiz(data);
      started.current = Date.now();
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  useEffect(() => {
    if (fetched.current === url) return;   // StrictMode double-invoke would otherwise create two attempts
    fetched.current = url;
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  async function submit() {
    if (!quiz) return;
    setBusy(true);
    setError(null);
    try {
      const { data } = await api.post<QuizResult>("/quiz/submit", {
        quiz_id: quiz.quiz_id, answers, time_seconds: Math.round((Date.now() - started.current) / 1000),
      });
      setResult(data);
      if (diagnostic) await refresh();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  if (error && !quiz) return <div><PageHeader title="Quiz" /><ErrorState message={error} onRetry={load} /></div>;
  if (!quiz) return <Loading label={diagnostic ? "Building your diagnostic" : "Building an adaptive quiz"} />;

  const answered = Object.keys(answers).length;
  const byId = Object.fromEntries((result?.results || []).map((r) => [r.question_id, r]));

  return (
    <div>
      <PageHeader
        title={diagnostic ? `Diagnostic: ${quiz.questions.length} questions` : `Quiz: ${quiz.topic}`}
        subtitle={diagnostic
          ? "Questions span every level of the roadmap. Answer what you can and skip what you don't know. There's no penalty for guessing wrong, but honest answers give a better starting point."
          : `Difficulty adapts to your level and mastery. This one is ${quiz.difficulty_label.toLowerCase()} with ${quiz.questions.length} questions.`}
        action={<Pill tone="marker">{quiz.difficulty_label}</Pill>}
      />

      {result && (
        <div className="mb-8 space-y-4">
          <Card>
            <div className="flex flex-wrap items-center gap-6">
              <div>
                <div className="text-sm text-ink-soft">Score</div>
                <div className="font-display text-5xl font-extrabold">{Math.round(result.score)}%</div>
                <div className="text-sm text-ink-soft">{result.correct} of {result.total} correct</div>
              </div>
              {result.placement && (
                <div className="min-w-[220px] flex-1">
                  <div className="text-sm text-ink-soft">Accuracy by level</div>
                  <ul className="mt-1 space-y-1">
                    {Object.entries(result.placement.level_accuracy).map(([lvl, acc]) => (
                      <li key={lvl} className="grid grid-cols-[110px_1fr_48px] items-center gap-2 text-sm">
                        <span>{lvl}</span>
                        <span className="h-2 rounded-full bg-grid"><span className="block h-2 rounded-full bg-ink" style={{ width: `${acc}%` }} /></span>
                        <span className="text-right font-mono text-xs">{Math.round(acc)}%</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {!!result.weak_concepts.length && (
                <div className="min-w-[220px] flex-1">
                  <div className="text-sm text-ink-soft">Concepts to revisit</div>
                  <div className="mt-1 flex flex-wrap gap-1.5">{result.weak_concepts.map((c) => <Pill key={c} tone="revise">{c}</Pill>)}</div>
                </div>
              )}
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {diagnostic ? (
                <button className="btn-marker" onClick={() => nav(`/my-roadmap/${skill}`)}>See my personalised roadmap</button>
              ) : (
                <>
                  <Link className="btn-primary" to={`/topics/${quiz.topic_id}`}>Back to topic</Link>
                  <button className="btn-ghost" onClick={() => { fetched.current = null; load(); }}>Try a new quiz</button>
                </>
              )}
              <Link className="btn-ghost" to="/dashboard">Dashboard</Link>
            </div>
          </Card>
          <LoopReport loop={result.loop} />
        </div>
      )}

      <ol className="space-y-4">
        {quiz.questions.map((q, qi) => {
          const r = byId[q.id];
          return (
            <li key={q.id} className="card p-5">
              <fieldset disabled={!!result}>
                <legend className="w-full">
                  <span className="text-xs font-bold text-ink-faint">Question {qi + 1} · {q.concept}</span>
                  <span className="mt-1 block font-bold"><QuestionText text={q.question} /></span>
                </legend>
                <div className="mt-3 grid gap-2">
                  {q.options.map((o, oi) => {
                    const chosen = answers[q.id] === oi;
                    const correct = r && r.answer_index === oi;
                    const wrongPick = r && chosen && !r.correct;
                    return (
                      <label key={oi} className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2 text-sm
                        ${correct ? "border-mastery bg-mastery-soft" : wrongPick ? "border-revise bg-revise-soft" : chosen ? "border-ink bg-marker-soft" : "border-rule bg-white hover:bg-grid"}`}>
                        <input type="radio" name={`q${q.id}`} className="mt-0.5 accent-ink" checked={chosen} onChange={() => setAnswers({ ...answers, [q.id]: oi })} />
                        <span className="flex-1"><QuestionText text={o} /></span>
                        {correct && <CheckCircle2 size={16} className="text-mastery" aria-label="Correct answer" />}
                        {wrongPick && <XCircle size={16} className="text-revise" aria-label="Your answer" />}
                      </label>
                    );
                  })}
                </div>
              </fieldset>
              {r && <p className={`mt-3 text-sm ${r.correct ? "text-mastery" : "text-revise"}`}><strong>{r.correct ? "Correct." : r.chosen == null ? "Skipped." : "Not quite."}</strong> <span className="text-ink-soft">{r.explanation}</span></p>}
            </li>
          );
        })}
      </ol>

      {!result && (
        <div className="sticky bottom-0 mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-rule bg-paper/95 py-4 backdrop-blur">
          <span className="flex items-center gap-2 text-sm text-ink-soft"><Clock size={15} aria-hidden /> {answered} of {quiz.questions.length} answered</span>
          {error && <span className="text-sm font-bold text-revise" role="alert">{error}</span>}
          <button className="btn-marker px-6" disabled={busy || answered === 0} onClick={submit}>{busy ? "Scoring…" : "Submit answers"}</button>
        </div>
      )}
    </div>
  );
}

function QuestionText({ text }: { text: string }) {
  return <>{text.split(/(`[^`]+`)/g).map((p, i) => p.startsWith("`") ? <code key={i} className="rounded bg-grid px-1 text-[13px]">{p.slice(1, -1)}</code> : <span key={i}>{p}</span>)}</>;
}
