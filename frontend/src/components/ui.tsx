import { AlertTriangle, Check, CircleDot, Loader2, Lock, RotateCcw, Star, Circle } from "lucide-react";
import type { ReactNode } from "react";
import type { Status } from "../api/types";
import { STATUS_LABEL, STATUS_STYLE } from "../lib/format";

export function PageHeader({ title, subtitle, action }: { title: ReactNode; subtitle?: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-3xl font-extrabold text-ink sm:text-4xl">{title}</h1>
        {subtitle && <p className="mt-1 max-w-2xl text-ink-soft">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Card({ title, action, children, className = "" }: { title?: ReactNode; action?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`card p-5 ${className}`}>
      {(title || action) && (
        <div className="mb-3 flex items-center justify-between gap-3">
          {title && <h2 className="text-lg font-bold">{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function StatusIcon({ status, size = 14 }: { status: Status; size?: number }) {
  const props = { size, "aria-hidden": true, strokeWidth: 2.5 };
  switch (status) {
    case "MASTERED": return <Star {...props} fill="currentColor" />;
    case "COMPLETED": return <Check {...props} />;
    case "IN_PROGRESS": return <CircleDot {...props} />;
    case "NEEDS_REVISION": return <RotateCcw {...props} />;
    case "LOCKED": return <Lock {...props} />;
    default: return <Circle {...props} />;
  }
}

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-bold ${STATUS_STYLE[status]}`}>
      <StatusIcon status={status} size={12} /> {STATUS_LABEL[status]}
    </span>
  );
}

export function MasteryBar({ value, className = "" }: { value: number; className?: string }) {
  const color = value >= 85 ? "bg-mastery" : value >= 70 ? "bg-mastery/70" : value >= 60 ? "bg-progress" : value > 0 ? "bg-marker" : "bg-rule";
  return (
    <div className={`h-2 w-full overflow-hidden rounded-full bg-grid ${className}`} role="meter" aria-valuenow={Math.round(value)} aria-valuemin={0} aria-valuemax={100} aria-label="Mastery">
      <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${Math.max(2, Math.min(100, value))}%` }} />
    </div>
  );
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="card p-4">
      <div className="text-sm text-ink-soft">{label}</div>
      <div className="mt-1 font-display text-2xl font-extrabold">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-faint">{hint}</div>}
    </div>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-ink-soft" role="status">
      <Loader2 className="animate-spin" size={18} aria-hidden /> {label}…
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="card flex flex-wrap items-center gap-3 border-revise/40 bg-revise-soft/60 p-4 text-revise" role="alert">
      <AlertTriangle size={18} aria-hidden />
      <span className="flex-1">{message}</span>
      {onRetry && <button className="btn-ghost" onClick={onRetry}>Try again</button>}
    </div>
  );
}

export function Empty({ title, children, action }: { title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="card p-8 text-center">
      <h2 className="text-xl font-bold">{title}</h2>
      {children && <div className="mx-auto mt-2 max-w-md text-ink-soft">{children}</div>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

export function Pill({ children, tone = "plain" }: { children: ReactNode; tone?: "plain" | "marker" | "mastery" | "revise" | "progress" }) {
  const t = { plain: "bg-grid text-ink-soft", marker: "bg-marker-soft text-ink", mastery: "bg-mastery-soft text-mastery", revise: "bg-revise-soft text-revise", progress: "bg-progress-soft text-progress" }[tone];
  return <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-bold ${t}`}>{children}</span>;
}
