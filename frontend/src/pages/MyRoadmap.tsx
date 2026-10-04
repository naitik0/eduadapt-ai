import { FolderGit2, GitBranch, Route as RouteIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { MyRoadmap as MyRoadmapT, ProjectInfo, Recommendation, RoadmapView, Status } from "../api/types";
import MetroLine from "../components/MetroLine";
import SkillTree from "../components/SkillTree";
import { Card, Empty, ErrorState, Loading, MasteryBar, PageHeader, StatusBadge } from "../components/ui";
import { STATUS_LABEL } from "../lib/format";
import { useApi } from "../lib/useApi";

/** /my-roadmap : list of the student's roadmaps (redirects to the active one when there is only one). */
export function MyRoadmaps() {
  const { data, error, loading, reload } = useApi<MyRoadmapT[]>("/student/roadmaps");
  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error || ""} onRetry={reload} />;
  const assessed = data.filter((r) => r.assessment_done);
  if (assessed.length === 1) return <Navigate to={`/my-roadmap/${assessed[0].skill}`} replace />;
  return (
    <div>
      <PageHeader title="My roadmaps" subtitle="Every skill you've started. The active one drives your dashboard, recommendations and study plan."
        action={<Link to="/skills" className="btn-primary">Add a skill</Link>} />
      {!data.length ? (
        <Empty title="No roadmaps yet" action={<Link className="btn-marker" to="/skills">Choose a skill</Link>}>Pick a skill and take its diagnostic.</Empty>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {data.map((r) => (
            <li key={r.skill} className="card p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">{r.skill_name}</h2>
                {r.is_active && <span className="rounded bg-marker px-2 text-xs font-bold">Active</span>}
              </div>
              <MasteryBar value={r.completion} className="mt-3" />
              <p className="mt-1 text-sm text-ink-soft">{Math.round(r.completion)}% complete · average mastery {Math.round(r.avg_mastery)}%</p>
              <div className="mt-4">
                {r.assessment_done ? <Link className="btn-primary" to={`/my-roadmap/${r.skill}`}>Open roadmap</Link>
                  : <Link className="btn-marker" to={`/quiz/diagnostic/${r.skill}`}>Take the diagnostic</Link>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

type Tab = "line" | "tree" | "projects";

export default function MyRoadmap() {
  const { skill } = useParams();
  const nav = useNavigate();
  const [tab, setTab] = useState<Tab>("line");
  const [filter, setFilter] = useState<Status | "ALL">("ALL");
  const rm = useApi<RoadmapView>(`/student/roadmap?skill=${skill}`, [skill]);
  const next = useApi<{ recommendation: Recommendation | null }>(`/student/roadmap/next-topic?skill=${skill}`, [skill]);
  const projects = useApi<ProjectInfo[]>(tab === "projects" ? `/projects?skill=${skill}` : null, [skill, tab]);
  const [activating, setActivating] = useState(false);
  const [actErr, setActErr] = useState<string | null>(null);

  useEffect(() => {
    if (rm.data && rm.data.assessment_done === false) nav(`/quiz/diagnostic/${skill}`, { replace: true });
  }, [rm.data, skill, nav]);

  if (rm.loading) return <Loading label="Loading roadmap" />;
  if (rm.status === 404) {
    return <Empty title="You haven't started this roadmap" action={<Link className="btn-marker" to="/skills">Choose a skill</Link>}>Start it from the skills page to take the diagnostic.</Empty>;
  }
  if (rm.error || !rm.data) return <ErrorState message={rm.error || ""} onRetry={rm.reload} />;
  const v = rm.data;
  const rec = next.data?.recommendation;
  const topicsById = Object.fromEntries(v.levels.flatMap((l) => l.topics).map((t) => [t.id, t]));
  const filtered: RoadmapView = filter === "ALL" ? v : { ...v, levels: v.levels.map((l) => ({ ...l, topics: l.topics.filter((t) => t.status === filter) })).filter((l) => l.topics.length) };

  async function activate() {
    setActivating(true);
    setActErr(null);
    try { await api.post("/student/roadmap/activate", { skill }); rm.reload(); next.reload(); }
    catch (e) { setActErr(errorMessage(e)); }
    finally { setActivating(false); }
  }

  return (
    <div className="space-y-6">
      <PageHeader title={v.title} subtitle={v.description}
        action={!v.is_active && <button className="btn-marker" onClick={activate} disabled={activating}>{activating ? "Switching…" : "Make this my active skill"}</button>} />
      {actErr && <ErrorState message={actErr} />}

      <div className="grid gap-4 md:grid-cols-[1fr_1.4fr]">
        <Card>
          <div className="flex items-baseline justify-between"><span className="text-sm text-ink-soft">Completion</span><span className="font-display text-2xl font-extrabold">{Math.round(v.completion)}%</span></div>
          <MasteryBar value={v.completion} className="mt-2" />
          <div className="mt-3 flex flex-wrap gap-1.5">
            {(["ALL", "MASTERED", "COMPLETED", "IN_PROGRESS", "NEEDS_REVISION", "AVAILABLE", "LOCKED"] as const).map((s) => (
              <button key={s} onClick={() => setFilter(s)} aria-pressed={filter === s}
                className={`rounded-full border px-2.5 py-0.5 text-xs font-bold ${filter === s ? "border-ink bg-ink text-paper" : "border-rule bg-white hover:bg-grid"}`}>
                {s === "ALL" ? `All ${v.total_topics}` : `${STATUS_LABEL[s]} ${v.status_counts[s] || 0}`}
              </button>
            ))}
          </div>
        </Card>
        {rec ? (
          <Card>
            <div className="text-xs font-bold text-ink-soft">Your next station</div>
            <Link to={`/topics/${rec.topic_id}`} className="mt-1 block text-xl font-bold"><span className="highlight">{rec.title}</span></Link>
            <p className="mt-2 text-sm text-ink-soft">{rec.reason}</p>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
              <StatusBadge status={rec.status} /> <span>{rec.difficulty}</span> <span>{rec.est_minutes} min</span> <span>score {Math.round(rec.score)}</span>
              <Link to={`/topics/${rec.topic_id}`} className="btn-marker ml-auto">Go to topic</Link>
            </div>
          </Card>
        ) : <Card><p className="text-ink-soft">No open topics. Check the projects tab.</p></Card>}
      </div>

      <div role="tablist" aria-label="Roadmap views" className="flex gap-1 border-b border-rule">
        {([["line", "Roadmap line", RouteIcon], ["tree", "Skill tree", GitBranch], ["projects", "Projects", FolderGit2]] as const).map(([k, label, Icon]) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}
            className={`-mb-px flex items-center gap-2 border-b-[3px] px-4 py-2 text-sm font-bold ${tab === k ? "border-ink text-ink" : "border-transparent text-ink-soft hover:text-ink"}`}>
            <Icon size={16} aria-hidden /> {label}
          </button>
        ))}
      </div>

      {tab === "line" && <MetroLine roadmap={filtered} currentTopicId={rec?.topic_id} />}
      {tab === "tree" && v.skill_tree && (
        <div>
          <p className="mb-2 text-sm text-ink-soft">Columns follow prerequisite depth. Hover or focus a topic to trace what it needs and what it unlocks. Dashed boxes are projects; the yellow bar is mastery.</p>
          <SkillTree tree={v.skill_tree} />
        </div>
      )}
      {tab === "projects" && (projects.loading ? <Loading /> : projects.error ? <ErrorState message={projects.error} /> : (
        <div className="grid gap-4 lg:grid-cols-2">
          {projects.data?.map((p) => {
            const t = topicsById[p.topic_id];
            return (
              <article key={p.id} className="card p-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-lg font-bold">{p.name}</h3>
                  {t && <StatusBadge status={t.status} />}
                </div>
                <p className="mt-1 text-sm text-ink-soft">{p.difficulty} · about {p.est_hours} h · needs {p.required_skills.join(", ")}</p>
                <h4 className="mt-3 text-sm font-bold">Milestones</h4>
                <ol className="ml-5 mt-1 list-decimal space-y-0.5 text-sm">{p.milestones.map((m) => <li key={m.order}>{m.title}</li>)}</ol>
                <Link to={`/topics/${p.topic_id}`} className={`mt-4 ${t?.status === "LOCKED" ? "btn-ghost" : "btn-primary"}`}>
                  {t?.status === "LOCKED" ? "See what unlocks it" : "Open project brief"}
                </Link>
              </article>
            );
          })}
        </div>
      ))}
    </div>
  );
}
