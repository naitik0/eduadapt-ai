import { Bot, Brain, CalendarCheck, ClipboardCheck, GitBranch, Route } from "lucide-react";
import { Link } from "react-router-dom";
import { PublicShell } from "../components/Layout";

const STOPS = [
  { t: "Variables", s: "done" }, { t: "Loops", s: "done" }, { t: "Functions", s: "done" },
  { t: "OOP", s: "now" }, { t: "Decorators", s: "locked" }, { t: "Async", s: "locked" },
];

const LOOP = ["Assessment", "Classification", "Personal roadmap", "Recommendation", "Learn with the tutor", "Quiz", "Update everything"];

export default function Landing() {
  return (
    <PublicShell>
      <main>
        <section className="mx-auto grid max-w-6xl items-center gap-12 px-4 pb-16 pt-8 sm:px-6 lg:grid-cols-[1.1fr_1fr]">
          <div>
            <h1 className="text-4xl font-extrabold leading-[1.05] sm:text-6xl">
              A programming roadmap that <span className="highlight">knows where you are</span>.
            </h1>
            <p className="mt-5 max-w-xl text-lg text-ink-soft">
              EduAdapt AI places you with a 20-question diagnostic, classifies how you learn, and recommends the next topic
              from 17 technology roadmaps. Every quiz updates your mastery, roadmap, recommendations and study plan.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-marker px-5 py-3 text-base">Take the diagnostic</Link>
              <Link to="/login" className="btn-ghost px-5 py-3 text-base">Try a demo student</Link>
            </div>
            <p className="mt-3 text-sm text-ink-faint">Demo: aarav@demo.eduadapt.ai / demo1234</p>
          </div>
          <div className="card p-6" aria-label="Example roadmap">
            <div className="mb-4 flex items-center justify-between">
              <span className="font-display text-lg font-bold">Python line</span>
              <span className="text-sm text-ink-soft">6 of 55 stations</span>
            </div>
            <ol className="relative ml-1">
              <span className="absolute bottom-3 left-[13px] top-3 w-[3px] rounded bg-progress/40" aria-hidden />
              {STOPS.map((x) => (
                <li key={x.t} className="relative flex items-center gap-4 pb-4 last:pb-0">
                  <span className={`z-10 h-7 w-7 rounded-full border-[3px] ${x.s === "done" ? "border-mastery bg-mastery" : x.s === "now" ? "border-progress bg-white ring-4 ring-marker" : "border-rule bg-grid"}`} />
                  <span className={`font-bold ${x.s === "locked" ? "text-ink-faint" : ""} ${x.s === "now" ? "highlight" : ""}`}>{x.t}</span>
                  <span className="text-xs text-ink-faint">{x.s === "done" ? "Mastered" : x.s === "now" ? "Recommended next · score 86" : "Needs OOP at 60%"}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="border-y border-rule bg-white/80">
          <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
            <h2 className="text-3xl font-extrabold">One loop, run after every quiz</h2>
            <ol className="mt-6 flex flex-wrap items-center gap-2">
              {LOOP.map((s, i) => (
                <li key={s} className="flex items-center gap-2">
                  <span className="rounded-lg border border-rule bg-paper px-3 py-2 font-bold">{s}</span>
                  {i < LOOP.length - 1 && <span className="text-ink-faint" aria-hidden>→</span>}
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <div className="grid gap-x-10 gap-y-8 md:grid-cols-3">
            {[
              { i: Brain, h: "Random Forest classifier", p: "Scores, attempts, pace and mastery decide your learning level, pace and how much support you get." },
              { i: GitBranch, h: "Hybrid recommendations", p: "Seven weighted signals rank every unlocked topic: knowledge gap, goal, prerequisites, recent results, interests, difficulty fit and your feedback." },
              { i: Route, h: "Prerequisites that hold", p: "Advanced topics stay locked until the topics they build on reach 60% mastery. No skipping ahead by accident." },
              { i: ClipboardCheck, h: "Adaptive quizzes", p: "Question count and difficulty follow your level and mastery. Missed concepts become your weak areas." },
              { i: Bot, h: "Grounded AI tutor", p: "Answers pull from a local FAISS knowledge base and know your topic, level and past mistakes. Works offline in mock mode." },
              { i: CalendarCheck, h: "Plans that re-plan", p: "Daily and weekly plans fit your available minutes and regenerate whenever your roadmap changes." },
            ].map(({ i: Icon, h, p }) => (
              <div key={h}>
                <Icon className="text-ink" size={26} aria-hidden />
                <h3 className="mt-3 text-lg font-bold">{h}</h3>
                <p className="mt-1 text-ink-soft">{p}</p>
              </div>
            ))}
          </div>
        </section>
        <footer className="border-t border-rule py-8 text-center text-sm text-ink-faint">EduAdapt AI · PS-002 Personalised Education</footer>
      </main>
    </PublicShell>
  );
}
