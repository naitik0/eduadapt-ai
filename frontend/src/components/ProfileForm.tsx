import { useState, type FormEvent } from "react";
import { api, errorMessage } from "../api/client";
import type { Profile } from "../api/types";
import { GOAL_LABEL, INTEREST_LABEL, PREFERENCE_LABEL } from "../lib/format";

export default function ProfileForm({ profile, submitLabel, onSaved }: { profile: Profile; submitLabel: string; onSaved: (p: Profile) => void }) {
  const [f, setF] = useState({
    name: profile.name, goal: profile.goal || "fundamentals", interests: profile.interests || [],
    daily_minutes: profile.daily_minutes || 60, target_date: profile.target_date || "",
    learning_preference: profile.learning_preference || "hands_on",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (i: string) => setF((x) => ({ ...x, interests: x.interests.includes(i) ? x.interests.filter((y) => y !== i) : [...x.interests, i] }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { data } = await api.put<Profile>("/student/profile", { ...f, target_date: f.target_date || null });
      onSaved(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-6">
      <div>
        <label className="label" htmlFor="pname">Name</label>
        <input id="pname" className="input max-w-sm" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
      </div>
      <fieldset>
        <legend className="label">What are you learning for?</legend>
        <div className="grid gap-2 sm:grid-cols-3">
          {profile.options.goals.map((g) => (
            <label key={g} className={`cursor-pointer rounded-lg border px-3 py-2 text-sm font-bold ${f.goal === g ? "border-ink bg-marker-soft" : "border-rule bg-white hover:bg-grid"}`}>
              <input type="radio" name="goal" value={g} checked={f.goal === g} onChange={() => setF({ ...f, goal: g })} className="sr-only" />
              {GOAL_LABEL[g] || g}
            </label>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="label">Interests <span className="font-normal text-ink-faint">(pick any)</span></legend>
        <div className="flex flex-wrap gap-2">
          {profile.options.interests.map((i) => (
            <button type="button" key={i} aria-pressed={f.interests.includes(i)} onClick={() => toggle(i)}
              className={`rounded-full border px-3 py-1 text-sm font-bold ${f.interests.includes(i) ? "border-ink bg-ink text-paper" : "border-rule bg-white hover:bg-grid"}`}>
              {INTEREST_LABEL[i] || i}
            </button>
          ))}
        </div>
      </fieldset>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="mins">Study time per day: {f.daily_minutes} min</label>
          <input id="mins" type="range" min={15} max={240} step={15} value={f.daily_minutes} onChange={(e) => setF({ ...f, daily_minutes: Number(e.target.value) })} className="w-full accent-ink" />
        </div>
        <div>
          <label className="label" htmlFor="target">Target date <span className="font-normal text-ink-faint">(optional)</span></label>
          <input id="target" type="date" className="input" value={f.target_date} onChange={(e) => setF({ ...f, target_date: e.target.value })} />
        </div>
      </div>
      <fieldset>
        <legend className="label">How do you learn best?</legend>
        <div className="grid gap-2 sm:grid-cols-3">
          {Object.entries(PREFERENCE_LABEL).map(([k, v]) => (
            <label key={k} className={`cursor-pointer rounded-lg border px-3 py-2 text-sm font-bold ${f.learning_preference === k ? "border-ink bg-marker-soft" : "border-rule bg-white hover:bg-grid"}`}>
              <input type="radio" name="pref" value={k} checked={f.learning_preference === k} onChange={() => setF({ ...f, learning_preference: k })} className="sr-only" />
              {v}
            </label>
          ))}
        </div>
      </fieldset>
      {error && <p className="text-sm font-bold text-revise" role="alert">{error}</p>}
      <button className="btn-primary" disabled={busy}>{busy ? "Saving…" : submitLabel}</button>
    </form>
  );
}
