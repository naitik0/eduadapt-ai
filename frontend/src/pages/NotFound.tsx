import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="text-5xl font-extrabold">Off the map</h1>
      <p className="mt-3 text-ink-soft">This page isn't on any roadmap.</p>
      <Link to="/" className="btn-primary mt-6">Go home</Link>
    </main>
  );
}
