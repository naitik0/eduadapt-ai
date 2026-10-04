import { BookOpen, CheckCircle2, Clock, ExternalLink, FileText, Hammer, ListChecks, PlayCircle, Video } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { LoopResult, Resource, TopicDetail } from "../api/types";
import LoopReport from "../components/LoopReport";
import TutorChat from "../components/TutorChat";
import { Card, ErrorState, Loading, MasteryBar, Pill, StatusBadge } from "../components/ui";
import { useApi } from "../lib/useApi";

const KIND_ICON: Record<string, typeof BookOpen> = { notes: FileText, video: Video, documentation: BookOpen, practice: Hammer, quiz: ListChecks, project: Hammer };

export function ResourceItem({ r }: { r: Resource }) {
  const Icon = KIND_ICON[r.kind] || FileText;
  const [open, setOpen] = useState(false);
  const external = r.url.startsWith("http");
  return (
    <li className="rounded-lg border border-rule bg-white p-3">
      <div className="flex items-start gap-3">
        <Icon size={18} className="mt-0.5 shrink-0 text-ink-soft" aria-hidden />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-bold">{r.title}</span>
            <Pill>{r.kind}</Pill>
            <span className="text-xs text-ink-faint">{r.est_minutes} min</span>
          </div>
          <p className="text-xs text-mastery">{r.why}</p>
          {open && r.content && <pre className="mt-2 whitespace-pre-wrap font-sans text-sm text-ink-soft">{r.content}</pre>}
        </div>
        {external ? (
          <a href={r.url} target="_blank" rel="noreferrer" className="btn-ghost px-2 py-1 text-xs">Open <ExternalLink size={12} aria-hidden /></a>
        ) : r.kind === "quiz" ? null : r.content ? (
          <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setOpen((o) => !o)} aria-expanded={open}>{open ? "Hide" : "Read"}</button>
        ) : null}
      </div>
    </li>
  );
}

export default function TopicPage() {
  const { id } = useParams();
  const { data: t, loading, error, reload } = useApi<TopicDetail>(`/topics/${id}`, [id]);
  const [loop, setLoop] = useState<LoopResult | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [actionErr, setActionErr] = useState<string | null>(null);

  async function act(kind: "start" | "complete" | "practice") {
    setBusy(kind);
    setActionErr(null);
    try {
      const { data } = await api.post<LoopResult>(`/topics/${id}/${kind}`);
      setLoop(data);
      reload();
    } catch (e) {
      setActionErr(errorMessage(e));
    } finally {
      setBusy(null);
    }
  }

  if (loading && !t) return <Loading label="Loading topic" />;
  if (error || !t) return <ErrorState message={error || "Topic not found"} onRetry={reload} />;
  const p = t.progress;
  const locked = p.status === "LOCKED";

  return (
    <div className="space-y-6">
      <nav className="text-sm text-ink-soft" aria-label="Breadcrumb">
        <Link to={`/my-roadmap/${t.skill}`} className="hover:underline">{t.skill_name} roadmap</Link> <span aria-hidden>/</span> {t.level}
      </nav>
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2"><StatusBadge status={p.status} />{t.is_project && <Pill tone="marker">Project</Pill>}</div>
          <h1 className="mt-2 text-4xl font-extrabold">{t.title}</h1>
          <p className="mt-2 text-lg text-ink-soft">{t.description}</p>
          <p className="mt-2 flex items-center gap-2 text-sm text-ink-soft"><Clock size={15} aria-hidden /> About {t.est_minutes} minutes</p>
        </div>
        <Card className="w-full sm:w-72">
          <div className="flex items-baseline justify-between"><span className="text-sm text-ink-soft">Your mastery</span><span className="font-display text-3xl font-extrabold">{Math.round(p.mastery)}%</span></div>
          <MasteryBar value={p.mastery} className="mt-2" />
          <dl className="mt-3 grid grid-cols-2 gap-y-1 text-sm">
            <dt className="text-ink-soft">Quiz attempts</dt><dd className="text-right font-bold">{p.attempts}</dd>
            <dt className="text-ink-soft">Last score</dt><dd className="text-right font-bold">{p.last_score == null ? "—" : `${Math.round(p.last_score)}%`}</dd>
            <dt className="text-ink-soft">Practice sets</dt><dd className="text-right font-bold">{p.practice_done}</dd>
          </dl>
        </Card>
      </header>

      {locked ? (
        <Card title="This topic is locked">
          <p className="text-ink-soft">Reach 60% mastery in each prerequisite to unlock it.</p>
          <ul className="mt-3 space-y-2">
            {t.prerequisites.map((pr) => (
              <li key={pr.id} className="flex items-center gap-3">
                {pr.met ? <CheckCircle2 size={16} className="text-mastery" aria-label="met" /> : <span className="h-4 w-4 rounded-full border-2 border-rule" aria-label="not met" />}
                <Link to={`/topics/${pr.id}`} className="font-bold hover:underline">{pr.title}</Link>
                <span className="text-sm text-ink-soft">{Math.round(pr.mastery)}% of {pr.min_mastery}% needed</span>
              </li>
            ))}
          </ul>
        </Card>
      ) : (
        <Card>
          <div className="flex flex-wrap items-center gap-2">
            <span className="mr-2 text-sm"><strong>Adaptive mode: {t.adaptive.difficulty}.</strong> <span className="text-ink-soft">{t.adaptive.approach}.</span></span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {p.status === "AVAILABLE" && <button className="btn-primary" disabled={!!busy} onClick={() => act("start")}><PlayCircle size={16} aria-hidden /> {busy === "start" ? "Starting…" : "Start learning"}</button>}
            <button className="btn-ghost" disabled={!!busy || p.learned} onClick={() => act("complete")}><BookOpen size={16} aria-hidden /> {p.learned ? "Lesson studied" : busy === "complete" ? "Saving…" : "Mark lesson as studied"}</button>
            <button className="btn-ghost" disabled={!!busy} onClick={() => act("practice")}><Hammer size={16} aria-hidden /> {busy === "practice" ? "Saving…" : "I finished a practice set"}</button>
            <Link className="btn-marker" to={`/quiz/${t.id}`}><ListChecks size={16} aria-hidden /> Take the {t.adaptive.difficulty.toLowerCase()} quiz</Link>
          </div>
          <p className="mt-2 text-xs text-ink-faint">Studying and practice raise mastery up to 68%. Passing the quiz is what completes a topic (70%+).</p>
          {actionErr && <div className="mt-3"><ErrorState message={actionErr} /></div>}
        </Card>
      )}

      {loop && <LoopReport loop={loop} />}

      <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <div className="space-y-6">
          <Card title="Learning objectives">
            <ul className="space-y-1.5">{t.objectives.map((o) => <li key={o} className="flex gap-2"><CheckCircle2 size={16} className="mt-0.5 shrink-0 text-mastery" aria-hidden />{o}</li>)}</ul>
            <h3 className="mb-2 mt-4 text-sm font-bold">Key concepts</h3>
            <div className="flex flex-wrap gap-1.5">{t.concepts.map((c) => <Pill key={c}>{c}</Pill>)}</div>
          </Card>
          <Card title="Resources for you" action={<span className="text-xs text-ink-faint">Ranked by your preference and level</span>}>
            <ul className="space-y-2">{t.resources.map((r) => <ResourceItem key={r.id} r={r} />)}</ul>
          </Card>
          {!!t.practice.length && (
            <Card title="Practice">
              <ol className="ml-5 list-decimal space-y-1.5">{t.practice.map((x) => <li key={x}>{x.replace(/^\d+\.\s*/, "")}</li>)}</ol>
            </Card>
          )}
          {t.project && (
            <Card title="Project brief">
              <p className="text-sm text-ink-soft">{t.project.difficulty} · about {t.project.est_hours} hours · uses {t.project.required_skills.join(", ")}</p>
              <h3 className="mt-3 text-sm font-bold">Requirements</h3>
              <ul className="ml-5 list-disc text-sm">{t.project.requirements.map((r) => <li key={r}>{r}</li>)}</ul>
              <h3 className="mt-3 text-sm font-bold">Milestones</h3>
              <ol className="ml-5 list-decimal text-sm">{t.project.milestones.map((m) => <li key={m.order}><strong>{m.title}.</strong> {m.description}</li>)}</ol>
              <h3 className="mt-3 text-sm font-bold">Evaluation criteria</h3>
              <ul className="ml-5 list-disc text-sm">{t.project.evaluation_criteria.map((r) => <li key={r}>{r}</li>)}</ul>
            </Card>
          )}
          <Card title="Where this fits">
            <div className="grid gap-4 sm:grid-cols-2 text-sm">
              <div>
                <h3 className="mb-1 font-bold">Builds on</h3>
                {t.prerequisites.length ? <ul className="space-y-1">{t.prerequisites.map((pr) => <li key={pr.id}><Link className="hover:underline" to={`/topics/${pr.id}`}>{pr.title}</Link> <span className="text-ink-faint">{Math.round(pr.mastery)}%</span></li>)}</ul> : <p className="text-ink-soft">No prerequisites.</p>}
              </div>
              <div>
                <h3 className="mb-1 font-bold">Unlocks</h3>
                {t.unlocks.length ? <ul className="space-y-1">{t.unlocks.map((u) => <li key={u.id}><Link className="hover:underline" to={`/topics/${u.id}`}>{u.title}</Link></li>)}</ul> : <p className="text-ink-soft">End of this branch.</p>}
              </div>
            </div>
          </Card>
        </div>
        <div>
          <h2 className="mb-2 text-lg font-bold">Ask the AI tutor</h2>
          <div className="lg:sticky lg:top-6"><TutorChat topicId={t.id} /></div>
        </div>
      </div>
    </div>
  );
}
