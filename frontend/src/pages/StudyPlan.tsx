import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { PlanItem, StudyPlan } from "../api/types";
import { Card, Empty, ErrorState, Loading, PageHeader, Stat } from "../components/ui";
import { ACTIVITY_LABEL, minutes, shortDate } from "../lib/format";
import { useApi } from "../lib/useApi";

export default function StudyPlanPage() {
  const { data, error, status, loading, reload, setData } = useApi<StudyPlan>("/study-plan");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function regenerate() {
    setBusy(true);
    setErr(null);
    try { setData((await api.post<StudyPlan>("/study-plan/generate")).data); }
    catch (e) { setErr(errorMessage(e)); }
    finally { setBusy(false); }
  }

  async function toggle(item: PlanItem) {
    if (!data) return;
    const flip = (d: StudyPlan, done: boolean): StudyPlan => {
      const upd = (items: PlanItem[]) => items.map((i) => (i.id === item.id ? { ...i, done } : i));
      return { ...d, today: { ...d.today, items: upd(d.today.items) }, week: d.week.map((w) => ({ ...w, items: upd(w.items) })) };
    };
    setData(flip(data, !item.done));
    try { await api.patch(`/study-plan/items/${item.id}`, { done: !item.done }); }
    catch (e) { setErr(errorMessage(e)); setData(flip(data, item.done)); }
  }

  if (loading) return <Loading label="Building your plan" />;
  if (status === 404) return <Empty title="No plan yet" action={<Link className="btn-marker" to="/skills">Choose a skill</Link>}>Start a roadmap and your plan appears here.</Empty>;
  if (error || !data) return <ErrorState message={error || ""} onRetry={reload} />;
  const s = data.summary;

  return (
    <div className="space-y-6">
      <PageHeader title="Study plan" subtitle="Built from your top recommendations, daily time, pace and support level. It re-plans automatically after quizzes, lessons and practice."
        action={<button className="btn-ghost" onClick={regenerate} disabled={busy}><RefreshCw size={16} className={busy ? "animate-spin" : ""} aria-hidden /> {busy ? "Re-planning…" : "Regenerate"}</button>} />
      {err && <ErrorState message={err} />}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Daily budget" value={minutes(data.daily_minutes)} />
        <Stat label="Work remaining" value={minutes(s.remaining_minutes)} hint={`${s.topics_scheduled} topics scheduled this week`} />
        <Stat label="Estimated completion" value={shortDate(s.estimated_completion)} hint={`${s.days_to_complete} study days`} />
        <Stat label="Target date" value={s.target_date ? shortDate(s.target_date) : "Not set"}
          hint={s.on_track == null ? <Link to="/profile" className="underline">Set one in your profile</Link> : s.on_track ? "On track" : `Needs about ${s.minutes_per_day_needed} min a day`} />
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.week.map((d) => {
          const done = d.items.filter((i) => i.done).length;
          return (
            <Card key={d.day} title={d.day === 0 ? "Today" : new Date(d.date + "T00:00:00").toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}
              action={<span className="text-xs text-ink-faint">{done}/{d.items.length} · {minutes(d.total_minutes)}</span>}
              className={d.day === 0 ? "border-ink/40" : ""}>
              {d.items.length ? (
                <ul className="space-y-1.5">
                  {d.items.map((i) => (
                    <li key={i.id}>
                      <label className={`flex cursor-pointer items-start gap-3 rounded-md px-1 py-1 hover:bg-grid ${i.done ? "text-ink-faint line-through" : ""}`}>
                        <input type="checkbox" className="mt-1 accent-ink" checked={i.done} onChange={() => toggle(i)} />
                        <span className="w-12 shrink-0 font-mono text-xs leading-6">{i.minutes}m</span>
                        <span className="text-sm leading-6"><strong>{ACTIVITY_LABEL[i.activity] || i.activity}</strong> · <Link to={`/topics/${i.topic_id}`} className="hover:underline">{i.topic}</Link></span>
                      </label>
                    </li>
                  ))}
                </ul>
              ) : <p className="text-sm text-ink-soft">Rest day, or nothing unlocked yet.</p>}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
