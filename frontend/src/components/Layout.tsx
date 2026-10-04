import { BookOpen, Bot, CalendarCheck, ChartLine, Compass, GraduationCap, LayoutDashboard, LogOut, Map, Menu, Shield, User, X, Library } from "lucide-react";
import { useState, type ReactNode } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/my-roadmap", label: "My roadmap", icon: Map },
  { to: "/study-plan", label: "Study plan", icon: CalendarCheck },
  { to: "/resources", label: "Resources", icon: Library },
  { to: "/tutor", label: "AI tutor", icon: Bot },
  { to: "/progress", label: "Progress", icon: ChartLine },
  { to: "/skills", label: "Skills", icon: GraduationCap },
  { to: "/roadmaps", label: "All roadmaps", icon: Compass },
  { to: "/profile", label: "Profile", icon: User },
];

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link to="/" className={`flex items-center gap-2 font-display text-xl font-extrabold text-ink ${className}`}>
      <img src="/favicon.svg" alt="" width={28} height={28} /> EduAdapt <span className="rounded bg-marker px-1 text-sm">AI</span>
    </Link>
  );
}

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const { profile } = useAuth();
  const items = profile?.role === "admin" ? [...NAV, { to: "/admin", label: "Admin", icon: Shield }] : NAV;
  return (
    <ul className="space-y-0.5">
      {items.map(({ to, label, icon: Icon }) => (
        <li key={to}>
          <NavLink to={to} onClick={onNavigate}
            className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-bold ${isActive ? "bg-ink text-paper" : "text-ink-soft hover:bg-grid hover:text-ink"}`}>
            <Icon size={17} aria-hidden /> {label}
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

export default function Layout({ children }: { children?: ReactNode }) {
  const { profile, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-marker focus:px-3 focus:py-1">Skip to content</a>
      <aside className="sticky top-0 hidden h-screen flex-col border-r border-rule bg-paper/95 p-4 lg:flex">
        <Logo className="mb-6 px-2" />
        <nav aria-label="Main" className="flex-1 overflow-y-auto"><NavItems /></nav>
        <div className="mt-4 border-t border-rule pt-4">
          <div className="px-2 text-sm font-bold">{profile?.name}</div>
          <div className="px-2 text-xs text-ink-faint">{profile?.learning_level} learner · {profile?.streak_days ?? 0}-day streak</div>
          <button className="mt-3 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-bold text-ink-soft hover:bg-grid" onClick={logout}>
            <LogOut size={17} aria-hidden /> Sign out
          </button>
        </div>
      </aside>
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-rule bg-paper/95 px-4 py-3 backdrop-blur lg:hidden">
        <Logo />
        <button className="btn-ghost px-2" onClick={() => setOpen(true)} aria-label="Open menu"><Menu size={20} /></button>
      </header>
      {open && (
        <div className="fixed inset-0 z-40 bg-ink/40 lg:hidden" onClick={() => setOpen(false)}>
          <nav aria-label="Main" className="h-full w-72 bg-paper p-4" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between"><Logo /><button className="btn-ghost px-2" onClick={() => setOpen(false)} aria-label="Close menu"><X size={20} /></button></div>
            <NavItems onNavigate={() => setOpen(false)} />
            <button className="mt-4 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-bold text-ink-soft hover:bg-grid" onClick={logout}><LogOut size={17} aria-hidden /> Sign out</button>
          </nav>
        </div>
      )}
      <main id="main" key={loc.pathname} className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-10">
        {children ?? <Outlet />}
      </main>
    </div>
  );
}

export function PublicShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5 sm:px-6">
        <Logo />
        <nav className="flex items-center gap-2" aria-label="Account">
          <Link to="/login" className="btn-ghost">Sign in</Link>
          <Link to="/register" className="btn-primary"><BookOpen size={16} aria-hidden /> Create account</Link>
        </nav>
      </header>
      {children}
    </div>
  );
}
