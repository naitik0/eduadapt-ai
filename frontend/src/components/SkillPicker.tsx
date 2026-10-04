import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { MyRoadmap, Skill } from "../api/types";
import { useApi } from "../lib/useApi";
import { ErrorState, Loading } from "./ui";

/** Choose a skill: new skills go to the diagnostic, skills already assessed become the active roadmap. */
export default function SkillPicker({ mine = [] }: { mine?: MyRoadmap[] }) {
  const nav = useNavigate();
  const { data, error, loading, reload } = useApi<Skill[]>("/skills");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function choose(slug: string) {
    setBusy(slug);
    setErr(null);
    try {
      const { data: r } = await api.post("/student/roadmap/initialize", { skill: slug });
      if (r.needs_assessment) nav(`/quiz/diagnostic/${slug}`);
      else { await api.post("/student/roadmap/activate", { skill: slug }); nav(`/my-roadmap/${slug}`); }
    } catch (e) {
      setErr(errorMessage(e));
    } finally {
      setBusy(null);
    }
  }

  if (loading) return <Loading label="Loading skills" />;
  if (error || !data) return <ErrorState message={error || "No skills"} onRetry={reload} />;
  const groups = data.reduce<Record<string, Skill[]>>((acc, s) => ({ ...acc, [s.category]: [...(acc[s.category] || []), s] }), {});
  return (
    <div className="space-y-6">
      {err && <ErrorState message={err} />}
      {Object.entries(groups).map(([cat, skills]) => (
        <section key={cat}>
          <h2 className="mb-2 text-lg font-bold">{cat}</h2>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {skills.map((s) => {
              const m = mine.find((x) => x.skill === s.slug);
              return (
                <li key={s.slug} className="card flex flex-col p-4">
                  <div className="flex items-baseline justify-between gap-2">
                    <h3 className="text-lg font-bold">{s.name}</h3>
                    <span className="text-xs text-ink-faint">{s.topics} topics</span>
                  </div>
                  <p className="mt-1 flex-1 text-sm text-ink-soft">{s.description}</p>
                  {m?.assessment_done && <p className="mt-2 text-xs font-bold text-mastery">{Math.round(m.completion)}% complete{m.is_active ? " · active" : ""}</p>}
                  <button className={`mt-3 ${m?.is_active ? "btn-ghost" : "btn-primary"}`} disabled={busy !== null} onClick={() => choose(s.slug)}>
                    {busy === s.slug ? "Opening…" : m?.assessment_done ? (m.is_active ? "Open roadmap" : "Switch to this skill") : "Start with the diagnostic"}
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
