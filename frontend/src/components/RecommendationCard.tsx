import { Clock, Gauge, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { Recommendation } from "../api/types";
import { COMPONENT_LABEL } from "../lib/format";
import { StatusBadge } from "./ui";

export default function RecommendationCard({ rec, onChanged, featured = false }: { rec: Recommendation; onChanged?: () => void; featured?: boolean }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [open, setOpen] = useState(featured);

  async function rate(rating: 1 | -1) {
    setBusy(true);
    setMsg(null);
    try {
      await api.post("/recommendations/feedback", { recommendation_id: rec.id, topic_id: rec.topic_id, rating });
      setMsg(rating > 0 ? "Thanks. Similar topics will rank a little higher." : "Noted. This topic will rank a little lower.");
      onChanged?.();
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className={`card p-5 ${featured ? "border-ink/30" : ""}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-bold text-ink-soft">{featured ? "Recommended next" : `Option ${rec.rank}`} · {rec.level}</div>
          <h3 className={`mt-0.5 font-bold ${featured ? "text-2xl" : "text-lg"}`}>
            <Link to={`/topics/${rec.topic_id}`} className={featured ? "highlight hover:underline" : "hover:underline"}>{rec.title}</Link>
          </h3>
        </div>
        <div className="text-right">
          <div className="font-display text-3xl font-extrabold leading-none">{Math.round(rec.score)}</div>
          <div className="text-xs text-ink-faint">match score</div>
        </div>
      </div>
      <p className="mt-3 text-ink-soft">{rec.reason}</p>
      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
        <StatusBadge status={rec.status} />
        <span className="inline-flex items-center gap-1"><Gauge size={14} aria-hidden /> {rec.difficulty}</span>
        <span className="inline-flex items-center gap-1"><Clock size={14} aria-hidden /> {rec.est_minutes} min</span>
        <span className="text-ink-soft">Current mastery {Math.round(rec.mastery)}%</span>
      </div>
      <button className="mt-3 text-sm font-bold text-progress underline-offset-2 hover:underline" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        {open ? "Hide score breakdown" : "Show score breakdown"}
      </button>
      {open && (
        <ul className="mt-2 space-y-1.5">
          {Object.entries(rec.contributions).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
            <li key={k} className="grid grid-cols-[150px_1fr_44px] items-center gap-2 text-sm">
              <span className="text-ink-soft">{COMPONENT_LABEL[k] || k}</span>
              <span className="h-2 rounded-full bg-grid"><span className="block h-2 rounded-full bg-ink" style={{ width: `${Math.min(100, (v / 30) * 100)}%` }} /></span>
              <span className="text-right font-mono text-xs">+{v.toFixed(1)}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Link to={`/topics/${rec.topic_id}`} className={featured ? "btn-marker" : "btn-primary"}>Start this topic</Link>
        <button className="btn-ghost" disabled={busy} onClick={() => rate(1)} aria-label="This recommendation is useful"><ThumbsUp size={15} aria-hidden /> Useful</button>
        <button className="btn-ghost" disabled={busy} onClick={() => rate(-1)} aria-label="Not for me right now"><ThumbsDown size={15} aria-hidden /> Not now</button>
        {msg && <span className="text-sm text-ink-soft" role="status">{msg}</span>}
      </div>
    </article>
  );
}
