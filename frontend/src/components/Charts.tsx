import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Analytics, Status } from "../api/types";
import { STATUS_LABEL, shortDate } from "../lib/format";

const INK = "#1E2A44", GRID = "#E9EEF5", FAINT = "#8792A8";
const tick = { fill: FAINT, fontSize: 12 };
const STATUS_COLOR: Record<Status, string> = {
  MASTERED: "#2E8B6E", COMPLETED: "#8FD0B8", IN_PROGRESS: "#3A63B8", NEEDS_REVISION: "#B83A4B", AVAILABLE: "#F5D547", LOCKED: "#DCE3EE",
};

export function TrendChart({ data }: { data: Analytics["trend"] }) {
  const rows = data.map((d) => ({ ...d, label: shortDate(d.date) }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: -18 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="label" tick={tick} tickLine={false} axisLine={false} interval="preserveStartEnd" />
        <YAxis yAxisId="s" domain={[0, 100]} tick={tick} tickLine={false} axisLine={false} />
        <YAxis yAxisId="c" orientation="right" allowDecimals={false} tick={tick} tickLine={false} axisLine={false} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line yAxisId="s" type="monotone" dataKey="avg_score" name="Avg quiz score" stroke={INK} strokeWidth={2.5} dot={{ r: 3 }} connectNulls />
        <Line yAxisId="c" type="stepAfter" dataKey="topics_completed" name="Topics completed (cumulative)" stroke="#2E8B6E" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function TopicMasteryChart({ data, height = 280 }: { data: Analytics["mastery_by_topic"]; height?: number }) {
  const rows = data.map((d) => ({ name: d.title.length > 18 ? d.title.slice(0, 17) + "…" : d.title, mastery: d.mastery, status: d.status }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={rows} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 8 }}>
        <CartesianGrid stroke={GRID} horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={tick} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="name" width={130} tick={{ ...tick, fill: INK }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => [`${Math.round(v)}%`, "Mastery"]} />
        <Bar dataKey="mastery" radius={[0, 4, 4, 0]} barSize={14}>
          {rows.map((r, i) => <Cell key={i} fill={STATUS_COLOR[r.status]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function LevelMasteryChart({ data }: { data: Analytics["level_performance"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="level" tick={tick} tickLine={false} axisLine={false} />
        <YAxis domain={[0, 100]} tick={tick} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => [`${Math.round(v)}%`, "Avg mastery"]} />
        <Bar dataKey="avg_mastery" fill={INK} radius={[4, 4, 0, 0]} barSize={36} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function SkillMasteryChart({ data }: { data: Analytics["skill_mastery"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="skill" tick={tick} tickLine={false} axisLine={false} />
        <YAxis domain={[0, 100]} tick={tick} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => `${Math.round(v)}%`} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="avg_mastery" name="Avg mastery" fill={INK} radius={[4, 4, 0, 0]} barSize={22} />
        <Bar dataKey="completion" name="Completion" fill="#2E8B6E" radius={[4, 4, 0, 0]} barSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function CompletionDonut({ counts, total }: { counts: Partial<Record<Status, number>>; total: number }) {
  const order: Status[] = ["MASTERED", "COMPLETED", "IN_PROGRESS", "NEEDS_REVISION", "AVAILABLE", "LOCKED"];
  const rows = order.filter((s) => counts[s]).map((s) => ({ name: STATUS_LABEL[s], value: counts[s]!, status: s }));
  const done = (counts.MASTERED || 0) + (counts.COMPLETED || 0);
  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={rows} dataKey="value" nameKey="name" innerRadius={62} outerRadius={92} paddingAngle={1.5} stroke="none">
            {rows.map((r) => <Cell key={r.status} fill={STATUS_COLOR[r.status]} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-3xl font-extrabold">{total ? Math.round((done / total) * 100) : 0}%</span>
        <span className="text-xs text-ink-faint">{done} of {total} done</span>
      </div>
      <ul className="mt-2 flex flex-wrap justify-center gap-x-3 gap-y-1 text-xs">
        {rows.map((r) => <li key={r.status} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: STATUS_COLOR[r.status] }} />{r.name} {r.value}</li>)}
      </ul>
    </div>
  );
}

export function QuizScoresChart({ data }: { data: Analytics["quiz_performance"] }) {
  const rows = data.map((d, i) => ({ ...d, n: i + 1, label: d.kind === "diagnostic" ? "Diagnostic" : d.topic }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="n" tick={tick} tickLine={false} axisLine={false} />
        <YAxis domain={[0, 100]} tick={tick} tickLine={false} axisLine={false} />
        <Tooltip labelFormatter={(_, p) => (p?.[0]?.payload?.label as string) || ""} formatter={(v: number) => [`${Math.round(v)}%`, "Score"]} />
        <Bar dataKey="score" radius={[4, 4, 0, 0]} barSize={18}>
          {rows.map((r, i) => <Cell key={i} fill={r.score >= 70 ? "#2E8B6E" : r.score >= 60 ? "#3A63B8" : "#B83A4B"} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
