import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Recommendation, TopicDetail } from "../api/types";
import { Card, Empty, ErrorState, Loading, PageHeader, StatusBadge } from "../components/ui";
import { useApi } from "../lib/useApi";
import { PREFERENCE_LABEL } from "../lib/format";
import { useAuth } from "../auth/AuthContext";
import { ResourceItem } from "./Topic";

/** Resources for the topics the recommender is pointing at right now, ranked for this learner. */
export default function Resources() {
  const { profile } = useAuth();
  const recs = useApi<{ recommendations: Recommendation[] }>("/recommendations");
  const [topics, setTopics] = useState<TopicDetail[] | null>(null);
  const [kind, setKind] = useState("all");

  useEffect(() => {
    if (!recs.data) return;
    Promise.all(recs.data.recommendations.slice(0, 4).map((r) => api.get<TopicDetail>(`/topics/${r.topic_id}`).then((x) => x.data)))
      .then(setTopics).catch(() => setTopics([]));
  }, [recs.data]);

  if (recs.loading || (recs.data && !topics)) return <Loading label="Matching resources" />;
  if (recs.status === 404) return <Empty title="No roadmap yet" action={<Link className="btn-marker" to="/skills">Choose a skill</Link>} />;
  if (recs.error) return <ErrorState message={recs.error} onRetry={recs.reload} />;
  const kinds = ["all", "notes", "video", "practice", "documentation", "quiz", "project"];

  return (
    <div className="space-y-6">
      <PageHeader title="Resources" subtitle={<>Notes, videos, practice, docs, quizzes and projects for your recommended topics, ranked for <strong>{PREFERENCE_LABEL[profile?.learning_preference || "hands_on"].toLowerCase()}</strong> at the <strong>{profile?.learning_level.toLowerCase()}</strong> level.</>} />
      <div className="flex flex-wrap gap-1.5" role="group" aria-label="Filter by type">
        {kinds.map((k) => (
          <button key={k} aria-pressed={kind === k} onClick={() => setKind(k)}
            className={`rounded-full border px-3 py-1 text-sm font-bold capitalize ${kind === k ? "border-ink bg-ink text-paper" : "border-rule bg-white hover:bg-grid"}`}>{k}</button>
        ))}
      </div>
      {topics?.map((t) => {
        const list = t.resources.filter((r) => kind === "all" || r.kind === kind);
        return (
          <Card key={t.id} title={<Link className="hover:underline" to={`/topics/${t.id}`}>{t.title}</Link>}
            action={<div className="flex items-center gap-2 text-sm"><StatusBadge status={t.progress.status} /><span className="text-ink-soft">{t.adaptive.difficulty}</span></div>}>
            {list.length ? <ul className="space-y-2">{list.map((r) => <ResourceItem key={r.id} r={r} />)}</ul> : <p className="text-sm text-ink-soft">No {kind} resources for this topic.</p>}
          </Card>
        );
      })}
    </div>
  );
}
