import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Logo } from "../components/Layout";
import ProfileForm from "../components/ProfileForm";
import SkillPicker from "../components/SkillPicker";
import { Loading } from "../components/ui";

export default function Onboarding() {
  const { profile, refresh, logout } = useAuth();
  const [step, setStep] = useState<1 | 2>(profile?.goal ? 2 : 1);
  if (!profile) return <Loading />;
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-4 py-5">
        <Logo />
        <button className="btn-ghost" onClick={logout}>Sign out</button>
      </header>
      <main className="mx-auto max-w-5xl px-4 pb-16">
        <ol className="mb-6 flex gap-2 text-sm font-bold" aria-label="Onboarding steps">
          {["Your goals", "Pick a skill", "Diagnostic"].map((s, i) => (
            <li key={s} className={`rounded-full px-3 py-1 ${i + 1 === step ? "bg-ink text-paper" : i + 1 < step ? "bg-mastery-soft text-mastery" : "bg-grid text-ink-faint"}`}>
              {i + 1}. {s}
            </li>
          ))}
        </ol>
        {step === 1 ? (
          <div className="card p-6">
            <h1 className="text-3xl font-extrabold">Hi {profile.name.split(" ")[0]}, what should we plan around?</h1>
            <p className="mb-6 mt-1 text-ink-soft">Your goal, interests and time shape which topics get recommended and how your study plan is paced.</p>
            <ProfileForm profile={profile} submitLabel="Save and choose a skill" onSaved={async () => { await refresh(); setStep(2); }} />
          </div>
        ) : (
          <div>
            <h1 className="text-3xl font-extrabold">Pick the skill to start with</h1>
            <p className="mb-6 mt-1 text-ink-soft">
              You'll take a 20-question diagnostic across the beginner, intermediate and advanced parts of that roadmap.
              It sets your starting mastery, learning level and first recommendation. You can add more skills later.
            </p>
            <SkillPicker />
            <button className="btn-ghost mt-6" onClick={() => setStep(1)}>Back to goals</button>
          </div>
        )}
      </main>
    </div>
  );
}
