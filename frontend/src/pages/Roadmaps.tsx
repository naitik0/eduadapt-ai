import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import type { RoadmapSummary, RoadmapView } from "../api/types";
import { ErrorState, Loading, PageHeader } from "../components/ui";
import { useApi } from "../lib/useApi";

function Detail({ skill }: { skill: string }) {
  const { data, loading, error } = useApi<RoadmapView>(`/roadmaps/${skill}`);
  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error || ""} />;
  return (
    <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {data.levels.map((l) => (
        <div key={l.name}>
          <h4 className="mb-1 text-sm font-bold">{l.name}</h4>
          <ol className="ml-5 list-decimal space-y-0.5 text-sm text-ink-soft">
            {l.topics.map((t) => (
              <li key={t.id}>
                <span className="text-ink">{t.title}</span>
                {t.prerequisites.length > 0 && <span className="text-xs text-ink-faint"> · after {t.prerequisites.map((p) => p.title).join(", ")}</span>}
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  );
}

export default function Roadmaps() {
  const { data, loading, error, reload } = useApi<RoadmapSummary[]>("/roadmaps");
  const [open, setOpen] = useState<string | null>(null);
  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error || ""} onRetry={reload} />;
  return (
    <div>
      <PageHeader title="All roadmaps" subtitle={`${data.length} technology-specific roadmaps, each running beginner → intermediate → advanced → projects with explicit prerequisites.`}
        action={<Link to="/skills" className="btn-primary">Start a skill</Link>} />
      <ul className="space-y-3">
        {data.map((r) => (
          <li key={r.skill} className="card p-5">
            <button className="flex w-full flex-wrap items-center justify-between gap-3 text-left" aria-expanded={open === r.skill} onClick={() => setOpen(open === r.skill ? null : r.skill)}>
              <div>
                <h2 className="text-xl font-bold">{r.skill_name} <span className="ml-1 text-sm font-normal text-ink-faint">{r.category}</span></h2>
                <p className="text-sm text-ink-soft">{r.description}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex gap-3 text-xs text-ink-soft">{r.levels.map((l) => <span key={l.name}><strong className="text-ink">{l.count}</strong> {l.name.toLowerCase()}</span>)}</div>
                <ChevronDown className={`transition-transform ${open === r.skill ? "rotate-180" : ""}`} size={18} aria-hidden />
              </div>
            </button>
            {open === r.skill && <Detail skill={r.skill} />}
          </li>
        ))}
      </ul>
    </div>
  );
}
