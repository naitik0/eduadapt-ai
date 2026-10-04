import { MessageSquarePlus } from "lucide-react";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import type { ChatSource, Recommendation } from "../api/types";
import TutorChat from "../components/TutorChat";
import { Card, PageHeader } from "../components/ui";
import { useApi } from "../lib/useApi";

interface SessionRow { id: number; topic: string | null; topic_id: number | null; created_at: string; messages: number; preview: string }
interface SessionFull { id: number; topic_id: number | null; messages: { role: "user" | "assistant"; content: string; sources: ChatSource[] | null }[] }

export default function Tutor() {
  const [params] = useSearchParams();
  const sessions = useApi<SessionRow[]>("/ai/sessions");
  const status = useApi<{ ai_mode: string; live_llm: boolean; provider: string | null; rag: { documents: number; index: string } }>("/ai/status");
  const next = useApi<{ recommendation: Recommendation | null }>("/student/roadmap/next-topic");
  const [active, setActive] = useState<number | null>(null);
  const [newTopic, setNewTopic] = useState<number | null>(params.get("topic") ? Number(params.get("topic")) : null);
  const full = useApi<SessionFull>(active ? `/ai/sessions/${active}` : null, [active]);

  const topicId = active ? full.data?.topic_id ?? null : newTopic ?? next.data?.recommendation?.topic_id ?? null;
  const topicTitle = active ? sessions.data?.find((s) => s.id === active)?.topic : next.data?.recommendation?.title;

  return (
    <div>
      <PageHeader title="AI tutor" subtitle={<>Retrieval over {status.data?.rag.documents ?? "…"} lessons and syllabus entries ({status.data?.rag.index}), personalised with your level, mastery and mistakes. Running in <strong>{status.data?.live_llm ? `real mode (${status.data.provider})` : "mock mode"}</strong>.</>} />
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <Card title="Conversations" action={<button className="btn-ghost px-2 py-1 text-xs" onClick={() => { setActive(null); setNewTopic(null); sessions.reload(); }}><MessageSquarePlus size={14} aria-hidden /> New</button>}>
          <ul className="space-y-1">
            {sessions.data?.map((s) => (
              <li key={s.id}>
                <button onClick={() => setActive(s.id)} className={`w-full rounded-md px-2 py-1.5 text-left text-sm ${active === s.id ? "bg-ink text-paper" : "hover:bg-grid"}`}>
                  <span className="block font-bold">{s.topic || "General"}</span>
                  <span className={`block truncate text-xs ${active === s.id ? "text-paper/70" : "text-ink-faint"}`}>{s.preview}</span>
                </button>
              </li>
            ))}
            {!sessions.data?.length && <li className="text-sm text-ink-soft">No conversations yet.</li>}
          </ul>
        </Card>
        <div>
          <p className="mb-2 text-sm text-ink-soft">{topicTitle ? <>Topic: <strong className="text-ink">{topicTitle}</strong></> : "General question about your active skill"}</p>
          {active && full.loading ? null : (
            <TutorChat key={active ?? `new-${topicId}`} topicId={topicId} sessionId={active}
              initial={active && full.data ? full.data.messages : []} onSession={() => sessions.reload()} height="h-[620px]" />
          )}
        </div>
      </div>
    </div>
  );
}
