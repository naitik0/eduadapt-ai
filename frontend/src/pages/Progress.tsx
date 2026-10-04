import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Analytics } from "../api/types";
import { SkillMasteryChart, TrendChart } from "../components/Charts";
import { Card, ErrorState, Loading, MasteryBar, PageHeader, StatusBadge } from "../components/ui";
import { useApi } from "../lib/useApi";

export default function ProgressPage() {
  const { data, error, loading, reload } = useApi<Analytics>("/analytics");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"order" | "low" | "high">("order");
  const rows = useMemo(() => {
    const r = (data?.mastery_by_topic || []).filter((t) => t.title.toLowerCase().includes(q.toLowerCase()));
    if (sort === "low") return [...r].sort((a, b) => a.mastery - b.mastery);
    if (sort === "high") return [...r].sort((a, b) => b.mastery - a.mastery);
    return r;
  }, [data, q, sort]);
  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error || ""} onRetry={reload} />;
  return (
    <div className="space-y-6">
      <PageHeader title="Progress" subtitle={`Every topic's mastery in your active roadmap, plus how you're doing across skills.`} />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Across skills">{data.skill_mastery.length ? <SkillMasteryChart data={data.skill_mastery} /> : <p className="text-sm text-ink-soft">No skills yet.</p>}</Card>
        <Card title="Last 14 days"><TrendChart data={data.trend} /></Card>
      </div>
      <Card title="Topic mastery" action={
        <div className="flex gap-2">
          <label className="sr-only" htmlFor="tsearch">Search topics</label>
          <input id="tsearch" className="input w-40 py-1" placeholder="Search" value={q} onChange={(e) => setQ(e.target.value)} />
          <label className="sr-only" htmlFor="tsort">Sort</label>
          <select id="tsort" className="input w-36 py-1" value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
            <option value="order">Roadmap order</option><option value="low">Lowest first</option><option value="high">Highest first</option>
          </select>
        </div>}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-rule text-left text-ink-soft"><th className="py-2 pr-3">Topic</th><th className="pr-3">Level</th><th className="pr-3">Status</th><th className="w-48 pr-3">Mastery</th><th className="pr-3 text-right">Attempts</th><th className="text-right">Last score</th></tr></thead>
            <tbody>
              {rows.map((t) => (
                <tr key={t.topic_id} className="border-b border-grid">
                  <td className="py-2 pr-3"><Link to={`/topics/${t.topic_id}`} className="font-bold hover:underline">{t.title}</Link></td>
                  <td className="pr-3 text-ink-soft">{t.level}</td>
                  <td className="pr-3"><StatusBadge status={t.status} /></td>
                  <td className="pr-3"><div className="flex items-center gap-2"><MasteryBar value={t.mastery} /><span className="w-9 text-right font-mono text-xs">{Math.round(t.mastery)}</span></div></td>
                  <td className="pr-3 text-right">{t.attempts}</td>
                  <td className="text-right">{t.last_score == null ? "—" : `${Math.round(t.last_score)}%`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
