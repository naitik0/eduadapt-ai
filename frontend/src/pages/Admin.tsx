import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import { Card, ErrorState, Loading, PageHeader, Stat } from "../components/ui";
import { COMPONENT_LABEL } from "../lib/format";
import { useApi } from "../lib/useApi";

interface Overview {
  counts: Record<string, number>;
  students: { id: number; name: string; email: string; role: string; level: string; pace: string; support: string; roadmaps: number }[];
  weights: Record<string, number>;
  model: { trained: boolean; trained_at?: string; n_samples?: number; data?: string; metrics?: Record<string, { accuracy: number; macro_f1: number; feature_importance: Record<string, number> }> };
  rag: { documents: number; dimensions: number; index: string };
  ai_mode: string;
}

export default function Admin() {
  const { data, error, loading, reload } = useApi<Overview>("/admin/overview");
  const [w, setW] = useState<Record<string, number>>({});
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  useEffect(() => { if (data) setW(data.weights); }, [data]);

  async function saveWeights() {
    setBusy("w"); setMsg(null);
    try { const { data: nw } = await api.put("/admin/weights", w); setW(nw); setMsg("Weights saved and normalised. They apply to every recommendation from now on."); }
    catch (e) { setMsg(errorMessage(e)); } finally { setBusy(null); }
  }
  async function retrain() {
    setBusy("r"); setMsg(null);
    try { await api.post("/admin/retrain"); setMsg("Model retrained on the synthetic dataset and reloaded."); reload(); }
    catch (e) { setMsg(errorMessage(e)); } finally { setBusy(null); }
  }

  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error || ""} onRetry={reload} />;
  const total = Object.values(w).reduce((a, b) => a + b, 0) || 1;
  return (
    <div className="space-y-6">
      <PageHeader title="Admin" subtitle="Tune the hybrid recommender, inspect the classifier and see who's learning." />
      {msg && <p className="card p-3 text-sm font-bold" role="status">{msg}</p>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(data.counts).map(([k, v]) => <Stat key={k} label={k.replace(/_/g, " ")} value={v} />)}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Recommendation weights" action={<button className="btn-primary" onClick={saveWeights} disabled={busy === "w"}>{busy === "w" ? "Saving…" : "Save weights"}</button>}>
          <ul className="space-y-3">
            {Object.entries(w).map(([k, v]) => (
              <li key={k}>
                <label className="flex justify-between text-sm" htmlFor={`w-${k}`}><span className="font-bold">{COMPONENT_LABEL[k] || k}</span><span className="font-mono text-xs">{((v / total) * 100).toFixed(0)}%</span></label>
                <input id={`w-${k}`} type="range" min={0} max={0.6} step={0.01} value={v} onChange={(e) => setW({ ...w, [k]: Number(e.target.value) })} className="w-full accent-ink" />
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-ink-faint">Weights are normalised to sum to 100% when saved.</p>
        </Card>
        <Card title="Classifier" action={<button className="btn-ghost" onClick={retrain} disabled={busy === "r"}><RefreshCw size={15} className={busy === "r" ? "animate-spin" : ""} aria-hidden /> {busy === "r" ? "Training…" : "Retrain"}</button>}>
          {data.model.trained ? (
            <>
              <p className="text-sm text-ink-soft">Random Forest trained {data.model.trained_at?.slice(0, 16).replace("T", " ")} on {data.model.n_samples} rows of {data.model.data}.</p>
              <table className="mt-3 w-full text-sm">
                <thead><tr className="text-left text-ink-soft"><th className="py-1">Target</th><th className="text-right">Accuracy</th><th className="text-right">Macro F1</th><th className="pl-4">Top feature</th></tr></thead>
                <tbody>
                  {Object.entries(data.model.metrics || {}).map(([k, m]) => (
                    <tr key={k} className="border-t border-grid"><td className="py-1 font-bold">{k.replace(/_/g, " ")}</td><td className="text-right">{(m.accuracy * 100).toFixed(1)}%</td><td className="text-right">{m.macro_f1.toFixed(3)}</td>
                      <td className="pl-4 text-ink-soft">{Object.entries(m.feature_importance).sort((a, b) => b[1] - a[1])[0]?.[0]}</td></tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : <p>Not trained yet. Retrain to create the model.</p>}
          <p className="mt-4 text-sm text-ink-soft">RAG index: {data.rag.documents} documents · {data.rag.dimensions} dimensions · {data.rag.index}. AI mode: <strong>{data.ai_mode}</strong>.</p>
        </Card>
      </div>
      <Card title="Learners">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-rule text-left text-ink-soft"><th className="py-2">Name</th><th>Email</th><th>Level</th><th>Pace</th><th>Support</th><th className="text-right">Roadmaps</th></tr></thead>
            <tbody>{data.students.map((s) => (
              <tr key={s.id} className="border-b border-grid"><td className="py-2 font-bold">{s.name}{s.role === "admin" && <span className="ml-1 text-xs text-ink-faint">admin</span>}</td><td className="text-ink-soft">{s.email}</td><td>{s.level}</td><td>{s.pace}</td><td>{s.support}</td><td className="text-right">{s.roadmaps}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
