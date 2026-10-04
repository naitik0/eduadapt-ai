import { BookMarked, Send } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, errorMessage } from "../api/client";
import type { ChatReply, ChatSource } from "../api/types";
import TutorText from "./TutorText";

interface Msg { role: "user" | "assistant"; content: string; sources?: ChatSource[] | null; mode?: string }

const SUGGESTIONS = ["Explain this simply", "Show me an example with code", "Give me an analogy", "Give me a practice question", "I'm stuck, give me a hint", "What are my weak points here?"];

export default function TutorChat({ topicId, sessionId: initialSession, initial = [], onSession, height = "h-[520px]" }:
  { topicId?: number | null; sessionId?: number | null; initial?: Msg[]; onSession?: (id: number) => void; height?: string }) {
  const [messages, setMessages] = useState<Msg[]>(initial);
  const [sessionId, setSessionId] = useState<number | null>(initialSession ?? null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => { setMessages(initial); setSessionId(initialSession ?? null); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [initialSession, topicId]);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }); }, [messages, busy]);

  async function send(message: string, e?: FormEvent) {
    e?.preventDefault();
    if (!message.trim() || busy) return;
    setMessages((m) => [...m, { role: "user", content: message }]);
    setText("");
    setBusy(true);
    setError(null);
    try {
      const { data } = await api.post<ChatReply>("/ai/chat", { message, topic_id: topicId ?? undefined, session_id: sessionId ?? undefined });
      setSessionId(data.session_id);
      onSession?.(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.answer, sources: data.sources, mode: data.mode }]);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={`card flex flex-col ${height}`}>
      <div className="flex-1 space-y-4 overflow-y-auto p-4" aria-live="polite">
        {!messages.length && (
          <div className="text-sm text-ink-soft">
            <p>Ask anything about {topicId ? "this topic" : "your current skill"}. The tutor knows your level, mastery, goal and recent mistakes, and grounds answers in the local knowledge base.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => <button key={s} className="rounded-full border border-rule bg-white px-3 py-1 text-sm font-bold text-ink hover:bg-grid" onClick={() => send(s)}>{s}</button>)}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "flex justify-end" : ""}>
            {m.role === "user" ? (
              <div className="max-w-[85%] rounded-xl rounded-br-sm bg-ink px-3 py-2 text-sm text-paper">{m.content}</div>
            ) : (
              <div className="max-w-[95%]">
                <TutorText text={m.content} />
                {!!m.sources?.length && (
                  <details className="mt-2 text-xs text-ink-soft">
                    <summary className="flex cursor-pointer items-center gap-1 font-bold"><BookMarked size={13} aria-hidden /> Retrieved from {m.sources.length} knowledge-base entries{m.mode ? ` · ${m.mode} mode` : ""}</summary>
                    <ul className="ml-5 mt-1 list-disc">{m.sources.map((s, k) => <li key={k}>{s.source} <span className="text-ink-faint">({s.score.toFixed(2)})</span></li>)}</ul>
                  </details>
                )}
              </div>
            )}
          </div>
        ))}
        {busy && <p className="text-sm text-ink-faint" role="status">Tutor is thinking…</p>}
        {error && <p className="text-sm font-bold text-revise" role="alert">{error}</p>}
        <div ref={end} />
      </div>
      <form onSubmit={(e) => send(text, e)} className="flex gap-2 border-t border-rule p-3">
        <label htmlFor="tutor-input" className="sr-only">Message the tutor</label>
        <input id="tutor-input" className="input" placeholder="Ask the tutor…" value={text} onChange={(e) => setText(e.target.value)} maxLength={4000} />
        <button className="btn-primary" disabled={busy || !text.trim()} aria-label="Send"><Send size={16} aria-hidden /></button>
      </form>
    </div>
  );
}
