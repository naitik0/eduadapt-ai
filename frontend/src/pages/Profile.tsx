import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import ProfileForm from "../components/ProfileForm";
import { Card, Loading, PageHeader } from "../components/ui";

const FEATURE_LABEL: Record<string, string> = {
  previous_score: "Earlier quiz average", recent_score: "Recent quiz average", attempts: "Quiz attempts", study_hours: "Study hours",
  completion_rate: "Completion rate", time_per_question: "Seconds per question", topic_mastery: "Average mastery", goal: "Goal (encoded)",
  interest: "Interest (encoded)", difficulty: "Difficulty reached",
};

export default function ProfilePage() {
  const { profile, refresh } = useAuth();
  const [saved, setSaved] = useState(false);
  if (!profile) return <Loading />;
  const f = profile.classification_features || {};
  return (
    <div className="space-y-6">
      <PageHeader title="Profile" subtitle={profile.email} />
      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <Card title="Learning preferences">
          <ProfileForm profile={profile} submitLabel="Save changes" onSaved={async () => { await refresh(); setSaved(true); setTimeout(() => setSaved(false), 3000); }} />
          {saved && <p className="mt-3 text-sm font-bold text-mastery" role="status">Saved. Recommendations and your study plan were updated.</p>}
        </Card>
        <Card title="How the classifier sees you">
          <dl className="grid grid-cols-3 gap-2 text-center">
            {[["Level", profile.learning_level], ["Pace", profile.learning_pace], ["Support", profile.support_level]].map(([k, v]) => (
              <div key={k} className="rounded-lg bg-grid p-3"><dt className="text-xs text-ink-soft">{k}</dt><dd className="font-display text-lg font-extrabold">{v}</dd></div>
            ))}
          </dl>
          <p className="mt-2 text-sm text-ink-soft">Random Forest confidence {Math.round(profile.classification_confidence * 100)}%. Updated after every learning event.</p>
          {Object.keys(f).length > 0 && (
            <table className="mt-4 w-full text-sm">
              <caption className="mb-1 text-left text-sm font-bold">Input features</caption>
              <tbody>{Object.entries(f).map(([k, v]) => <tr key={k} className="border-b border-grid"><td className="py-1 text-ink-soft">{FEATURE_LABEL[k] || k}</td><td className="text-right font-mono text-xs">{v}</td></tr>)}</tbody>
            </table>
          )}
        </Card>
      </div>
    </div>
  );
}
