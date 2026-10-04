import { Link } from "react-router-dom";
import type { RoadmapView, Status, TopicNode } from "../api/types";
import { StatusIcon } from "./ui";
import { STATUS_LABEL } from "../lib/format";

/** The roadmap drawn as a transit line: each level is a line segment, each topic a station. */
const STATION: Record<Status, string> = {
  MASTERED: "bg-mastery border-mastery text-white",
  COMPLETED: "bg-white border-mastery text-mastery",
  IN_PROGRESS: "bg-progress border-progress text-white",
  NEEDS_REVISION: "bg-white border-revise text-revise",
  AVAILABLE: "bg-white border-ink text-ink",
  LOCKED: "bg-grid border-rule text-ink-faint",
};

const LINE_COLOR: Record<string, string> = {
  Beginner: "#2E8B6E", Intermediate: "#3A63B8", Advanced: "#7A4FB0", Projects: "#C07A1C",
};

function Station({ t, current }: { t: TopicNode; current: boolean }) {
  const locked = t.status === "LOCKED";
  return (
    <li className="relative flex items-start gap-4 pb-5 last:pb-0">
      <span className={`relative z-10 mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-[3px] ${STATION[t.status]} ${current ? "ring-4 ring-marker" : ""}`}>
        <StatusIcon status={t.status} size={13} />
      </span>
      <Link to={`/topics/${t.id}`}
        className={`group -mt-0.5 flex min-w-0 flex-1 flex-wrap items-baseline gap-x-3 gap-y-1 rounded-md px-2 py-1 hover:bg-grid ${locked ? "text-ink-faint" : ""}`}
        aria-label={`${t.title}, ${STATUS_LABEL[t.status]}, mastery ${Math.round(t.mastery)} percent`}>
        <span className={`font-bold ${current ? "highlight" : ""}`}>{t.title}</span>
        {t.is_project && <span className="rounded bg-marker-soft px-1.5 text-xs font-bold text-ink">Project</span>}
        <span className="text-xs text-ink-faint">{STATUS_LABEL[t.status]} · {Math.round(t.mastery)}% · {t.est_minutes} min</span>
        {locked && t.prerequisites.length > 0 && (
          <span className="w-full text-xs text-ink-faint">Needs {t.prerequisites.map((p) => p.title).join(", ")} at {t.prerequisites[0].min_mastery}%</span>
        )}
      </Link>
    </li>
  );
}

export default function MetroLine({ roadmap, currentTopicId }: { roadmap: RoadmapView; currentTopicId?: number }) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {roadmap.levels.map((lvl) => {
        const done = lvl.topics.filter((t) => t.status === "COMPLETED" || t.status === "MASTERED").length;
        return (
          <section key={lvl.name} className="card p-5" aria-label={`${lvl.name} level`}>
            <header className="mb-4 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-lg font-bold">
                <span className="inline-block h-3 w-8 rounded-full" style={{ background: LINE_COLOR[lvl.name] }} aria-hidden />
                {lvl.name}
              </h3>
              <span className="text-sm text-ink-soft">{done} of {lvl.topics.length} done</span>
            </header>
            <ol className="relative">
              <span className="absolute bottom-3 left-[13px] top-3 w-[3px] rounded" style={{ background: LINE_COLOR[lvl.name], opacity: 0.35 }} aria-hidden />
              {lvl.topics.map((t) => <Station key={t.id} t={t} current={t.id === currentTopicId} />)}
            </ol>
          </section>
        );
      })}
    </div>
  );
}
