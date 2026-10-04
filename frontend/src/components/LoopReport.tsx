import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import type { LoopResult } from "../api/types";
import { STATUS_LABEL } from "../lib/format";

const STEP_LABEL: Record<string, string> = {
  learning_event: "Learning event", performance_update: "Performance", classification_update: "Classification",
  mastery_update: "Mastery", roadmap_update: "Roadmap", recommendation_update: "Recommendation", study_plan_update: "Study plan",
};

/** Shows what the live feedback loop changed after an action: the before/after of every stage. */
export default function LoopReport({ loop, compact = false }: { loop: LoopResult; compact?: boolean }) {
  if (!loop.pipeline) return null;
  const m = loop.mastery_change;
  return (
    <div className="card border-ink/20 p-5" aria-live="polite">
      <h3 className="flex items-center gap-2 text-lg font-bold"><Sparkles size={18} aria-hidden /> What changed</h3>
      <ol className="mt-3 flex flex-wrap items-center gap-1.5 text-xs">
        {loop.pipeline.map((s, i) => (
          <li key={s} className="flex items-center gap-1.5">
            <span className="rounded-md bg-mastery-soft px-2 py-1 font-bold text-mastery">{STEP_LABEL[s] || s}</span>
            {i < loop.pipeline!.length - 1 && <ArrowRight size={12} className="text-ink-faint" aria-hidden />}
          </li>
        ))}
      </ol>
      <dl className={`mt-4 grid gap-4 ${compact ? "" : "sm:grid-cols-2"}`}>
        {m && (
          <div>
            <dt className="text-sm text-ink-soft">Mastery of {m.topic}</dt>
            <dd className="font-display text-2xl font-extrabold">
              {Math.round(m.before)}% <span className="text-ink-faint">→</span>{" "}
              <span className={m.after >= m.before ? "text-mastery" : "text-revise"}>{Math.round(m.after)}%</span>
            </dd>
          </div>
        )}
        {loop.classification && (
          <div>
            <dt className="text-sm text-ink-soft">Classification {loop.classification_changed ? "(updated)" : "(unchanged)"}</dt>
            <dd className="font-bold">
              {loop.classification.learning_level} · {loop.classification.learning_pace} pace · {loop.classification.support_level} support
              <span className="ml-1 text-xs font-normal text-ink-faint">{Math.round(loop.classification.confidence * 100)}% confidence</span>
            </dd>
          </div>
        )}
        {!!loop.status_changes?.length && (
          <div>
            <dt className="text-sm text-ink-soft">Roadmap updates</dt>
            <dd>
              <ul className="mt-1 space-y-0.5 text-sm">
                {loop.status_changes.slice(0, 6).map((c) => (
                  <li key={c.topic_id}><strong>{c.topic}</strong>: {STATUS_LABEL[c.from]} → {STATUS_LABEL[c.to]}</li>
                ))}
                {loop.status_changes.length > 6 && <li className="text-ink-faint">and {loop.status_changes.length - 6} more</li>}
              </ul>
            </dd>
          </div>
        )}
        {!!loop.unlocked?.length && (
          <div>
            <dt className="text-sm text-ink-soft">Newly unlocked</dt>
            <dd className="mt-1 flex flex-wrap gap-1.5">
              {loop.unlocked.map((u) => <span key={u} className="rounded-md bg-marker px-2 py-0.5 text-sm font-bold">{u}</span>)}
            </dd>
          </div>
        )}
        {loop.recommendation && (
          <div className={compact ? "" : "sm:col-span-2"}>
            <dt className="text-sm text-ink-soft">
              Next recommendation {loop.recommendation_changed ? `(was ${loop.previous_recommendation})` : "(unchanged)"}
            </dt>
            <dd className="mt-1 flex flex-wrap items-center gap-3">
              <span className="font-bold">{loop.recommendation.title}</span>
              <span className="text-sm text-ink-soft">score {loop.recommendation.score}</span>
              <Link className="btn-marker" to={`/topics/${loop.recommendation.topic_id}`}>Open next topic</Link>
            </dd>
          </div>
        )}
      </dl>
    </div>
  );
}
