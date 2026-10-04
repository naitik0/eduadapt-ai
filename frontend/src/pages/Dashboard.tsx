import { Flame, Target } from "lucide-react";
import { Link } from "react-router-dom";
import type { Analytics, Recommendation, RoadmapView, StudyPlan } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { CompletionDonut, LevelMasteryChart, QuizScoresChart, TopicMasteryChart, TrendChart } from "../components/Charts";
import RecommendationCard from "../components/RecommendationCard";
import { Card, Empty, ErrorState, Loading, MasteryBar, PageHeader, Pill, Stat, StatusBadge } from "../components/ui";
import { ACTIVITY_LABEL, GOAL_LABEL, minutes, shortDate } from "../lib/format";
import { useApi } from "../lib/useApi";

export default function Dashboard() {
  const { profile } = useAuth();
  const a = useApi<Analytics>("/analytics");
  const recs = useApi<{ recommendations: Recommendation[] }>(a.data?.active_skill ? "/recommendations" : null, [a.data?.active_skill]);
  const plan = useApi<StudyPlan>(a.data?.active_skill ? "/study-plan" : null, [a.data?.active_skill]);
  const rm = useApi<RoadmapView>(a.data?.active_skill ? "/student/roadmap" : null, [a.data?.active_skill]);

  if (a.loading) return <Loading label="Loading your dashboard" />;
  if (a.error || !a.data) return <ErrorState message={a.error || "No data"} onRetry={a.reload} />;
  const d = a.data;
  if (!d.active_skill) {
    return (
      <div>
        <PageHeader title={`Welcome, ${profile?.name.split(" ")[0]}`} />
        <Empty title="Pick a skill to get your roadmap" action={<Link className="btn-marker" to="/skills">Choose a skill</Link>}>
          A short diagnostic places you on the roadmap and powers every recommendation here.
        </Empty>
      </div>
    );
  }

  const reloadAll = () => { a.reload(); recs.reload(); plan.reload(); rm.reload(); };
  const top = recs.data?.recommendations[0];
  const started = d.mastery_by_topic.filter((t) => t.attempts > 0 || (t.mastery > 0 && t.status !== "LOCKED"))
    .sort((x, y) => y.mastery - x.mastery).slice(0, 12);
  const current = rm.data?.levels.flatMap((l) => l.topics).find((t) => t.status === "IN_PROGRESS");
  const todayDone = plan.data?.today.items.filter((i) => i.done).length ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title={<>Hi {d.profile.name.split(" ")[0]}, here's your <span className="highlight">{rm.data?.skill_name || d.active_skill}</span> week</>}
        subtitle={<>Goal: {GOAL_LABEL[d.profile.goal] || "not set"} · {d.profile.daily_minutes} min a day</>}
        action={<Link to={`/my-roadmap/${d.active_skill}`} className="btn-primary">Open my roadmap</Link>}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Roadmap progress" value={`${Math.round(d.overall_progress)}%`} hint={`${d.topics_done} of ${d.topics_total} topics completed`} />
        <Stat label="Learning level" value={d.profile.learning_level}
          hint={`${d.profile.learning_pace} pace · ${d.profile.support_level} support · ${Math.round(d.profile.confidence * 100)}% confidence`} />
        <Stat label="Learning streak" value={<span className="inline-flex items-center gap-2"><Flame className="text-revise" size={22} aria-hidden />{d.profile.streak_days} days</span>} hint="Any learning activity keeps it going" />
        <Stat label="Estimated completion" value={plan.data ? shortDate(plan.data.summary.estimated_completion) : "—"}
          hint={plan.data ? `${minutes(plan.data.summary.remaining_minutes)} left at your pace` : undefined} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        {top ? <RecommendationCard rec={top} featured onChanged={reloadAll} />
          : recs.loading ? <Loading /> : <Card><p>Every available topic is complete. Try a project from your roadmap.</p></Card>}
        <Card title="Today's plan" action={<Link to="/study-plan" className="text-sm font-bold text-progress hover:underline">Full week</Link>}>
          {plan.data ? (
            <>
              <p className="-mt-1 mb-3 text-sm text-ink-soft">{todayDone} of {plan.data.today.items.length} done · {minutes(plan.data.today.total_minutes)}</p>
              <ul className="space-y-2">
                {plan.data.today.items.map((i) => (
                  <li key={i.id} className={`flex items-center gap-3 text-sm ${i.done ? "text-ink-faint line-through" : ""}`}>
                    <span className="w-14 shrink-0 font-mono text-xs">{i.minutes} min</span>
                    <span><strong>{ACTIVITY_LABEL[i.activity] || i.activity}</strong> · <Link className="hover:underline" to={`/topics/${i.topic_id}`}>{i.topic}</Link></span>
                  </li>
                ))}
              </ul>
            </>
          ) : <Loading />}
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Currently learning">
          {current ? (
            <div>
              <Link to={`/topics/${current.id}`} className="text-lg font-bold hover:underline">{current.title}</Link>
              <MasteryBar value={current.mastery} className="mt-2" />
              <p className="mt-1 text-sm text-ink-soft">{Math.round(current.mastery)}% mastery</p>
            </div>
          ) : <p className="text-sm text-ink-soft">Nothing in progress. Start the recommended topic above.</p>}
          <h3 className="mb-2 mt-5 text-sm font-bold">Weak areas</h3>
          {d.weak_areas.length ? (
            <ul className="space-y-2">
              {d.weak_areas.slice(0, 5).map((w) => (
                <li key={w.topic_id} className="flex items-center justify-between gap-2 text-sm">
                  <Link to={`/topics/${w.topic_id}`} className="truncate hover:underline">{w.title}</Link>
                  <StatusBadge status={w.status} />
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-ink-soft">No weak areas yet.</p>}
          {!!d.weak_concepts.length && (
            <div className="mt-3 flex flex-wrap gap-1.5">{d.weak_concepts.slice(0, 6).map((c) => <Pill key={c.concept} tone="revise">{c.concept}</Pill>)}</div>
          )}
        </Card>
        <Card title="Roadmap completion"><CompletionDonut counts={d.status_counts} total={d.topics_total} /></Card>
        <Card title="Mastery by level"><LevelMasteryChart data={d.level_performance} /></Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Progress trend" action={<span className="text-xs text-ink-faint">Last 14 days</span>}><TrendChart data={d.trend} /></Card>
        <Card title="Quiz performance" action={<span className="text-sm text-ink-soft">Average {Math.round(d.quiz_avg ?? 0)}%</span>}>
          {d.quiz_performance.length ? <QuizScoresChart data={d.quiz_performance} /> : <p className="text-sm text-ink-soft">No quizzes yet.</p>}
        </Card>
      </div>

      <Card title="Mastery by topic" action={<Link to="/progress" className="text-sm font-bold text-progress hover:underline">All topics</Link>}>
        {started.length ? <TopicMasteryChart data={started} height={Math.max(180, started.length * 26)} /> : <p className="text-sm text-ink-soft">Take a quiz to see topic mastery.</p>}
      </Card>

      {recs.data && recs.data.recommendations.length > 1 && (
        <section>
          <h2 className="mb-3 flex items-center gap-2 text-xl font-bold"><Target size={20} aria-hidden /> Other good next steps</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {recs.data.recommendations.slice(1, 3).map((r) => <RecommendationCard key={r.id} rec={r} onChanged={reloadAll} />)}
          </div>
        </section>
      )}
    </div>
  );
}
