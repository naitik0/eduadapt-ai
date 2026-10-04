import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { PublicShell } from "../components/Layout";

const DEMOS = [
  ["aarav@demo.eduadapt.ai", "Aarav", "Beginner · Python"],
  ["meera@demo.eduadapt.ai", "Meera", "Intermediate · Python"],
  ["rohan@demo.eduadapt.ai", "Rohan", "Advanced · Java"],
  ["sana@demo.eduadapt.ai", "Sana", "Beginner · C++"],
  ["kabir@demo.eduadapt.ai", "Kabir", "Intermediate · JavaScript"],
];

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <PublicShell>
      <main className="mx-auto max-w-md px-4 pb-16 pt-6">
        <div className="card p-7">
          <h1 className="text-3xl font-extrabold">{title}</h1>
          {children}
        </div>
      </main>
    </PublicShell>
  );
}

export function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const loc = useLocation() as { state?: { from?: string } };
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function go(e?: FormEvent, creds?: [string, string]) {
    e?.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const p = await login(...(creds ?? [email, password]));
      nav(p.onboarded || p.role === "admin" ? loc.state?.from || "/dashboard" : "/onboarding", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Shell title="Sign in">
      <form className="mt-6 space-y-4" onSubmit={go}>
        <div><label className="label" htmlFor="email">Email</label><input id="email" className="input" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div><label className="label" htmlFor="password">Password</label><input id="password" className="input" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        {error && <p className="text-sm font-bold text-revise" role="alert">{error}</p>}
        <button className="btn-primary w-full py-2.5" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
      <p className="mt-4 text-sm text-ink-soft">New here? <Link className="font-bold text-progress hover:underline" to="/register">Create an account</Link></p>
      <div className="mt-6 border-t border-rule pt-5">
        <h2 className="text-base font-bold">Or explore as a demo student</h2>
        <ul className="mt-3 grid gap-2">
          {DEMOS.map(([mail, name, tag]) => (
            <li key={mail}>
              <button type="button" disabled={busy} onClick={() => go(undefined, [mail, "demo1234"])}
                className="flex w-full items-center justify-between rounded-lg border border-rule bg-white px-3 py-2 text-left hover:bg-grid">
                <span className="font-bold">{name}</span><span className="text-sm text-ink-soft">{tag}</span>
              </button>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-ink-faint">Admin: admin@eduadapt.ai / admin1234</p>
      </div>
    </Shell>
  );
}

export function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(f.name, f.email, f.password);
      nav("/onboarding", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Shell title="Create your account">
      <p className="mt-1 text-ink-soft">Next you'll set your goal and take a short diagnostic.</p>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <div><label className="label" htmlFor="name">Name</label><input id="name" className="input" required autoComplete="name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></div>
        <div><label className="label" htmlFor="remail">Email</label><input id="remail" className="input" type="email" required autoComplete="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></div>
        <div>
          <label className="label" htmlFor="rpass">Password</label>
          <input id="rpass" className="input" type="password" minLength={8} required autoComplete="new-password" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} />
          <p className="mt-1 text-xs text-ink-faint">At least 8 characters.</p>
        </div>
        {error && <p className="text-sm font-bold text-revise" role="alert">{error}</p>}
        <button className="btn-primary w-full py-2.5" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
      </form>
      <p className="mt-4 text-sm text-ink-soft">Already have an account? <Link className="font-bold text-progress hover:underline" to="/login">Sign in</Link></p>
    </Shell>
  );
}
