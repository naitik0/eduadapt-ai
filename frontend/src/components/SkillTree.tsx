import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { RoadmapView, Status, TreeNode } from "../api/types";
import { STATUS_LABEL } from "../lib/format";

const FILL: Record<Status, string> = {
  MASTERED: "#2E8B6E", COMPLETED: "#D5EEE5", IN_PROGRESS: "#3A63B8", NEEDS_REVISION: "#F6DDE0",
  AVAILABLE: "#FFFFFF", LOCKED: "#E9EEF5",
};
const TEXT: Record<Status, string> = {
  MASTERED: "#FFFFFF", COMPLETED: "#1E2A44", IN_PROGRESS: "#FFFFFF", NEEDS_REVISION: "#B83A4B",
  AVAILABLE: "#1E2A44", LOCKED: "#8792A8",
};
const W = 168, H = 40, GX = 56, GY = 14;

/** Prerequisite graph laid out by depth (columns); hover a node to trace its prerequisites and unlocks. */
export default function SkillTree({ tree }: { tree: NonNullable<RoadmapView["skill_tree"]> }) {
  const nav = useNavigate();
  const [hover, setHover] = useState<number | null>(null);

  const { pos, width, height } = useMemo(() => {
    const cols = new Map<number, TreeNode[]>();
    tree.nodes.forEach((n) => cols.set(n.depth, [...(cols.get(n.depth) || []), n]));
    const pos = new Map<number, { x: number; y: number }>();
    let maxRows = 0;
    [...cols.keys()].sort((a, b) => a - b).forEach((d) => {
      const col = cols.get(d)!;
      maxRows = Math.max(maxRows, col.length);
      col.forEach((n, i) => pos.set(n.id, { x: 16 + d * (W + GX), y: 16 + i * (H + GY) }));
    });
    return { pos, width: 32 + cols.size * (W + GX) - GX, height: 32 + maxRows * (H + GY) - GY };
  }, [tree]);

  const related = useMemo(() => {
    if (hover == null) return null;
    const s = new Set<number>([hover]);
    const up = (id: number) => tree.edges.filter((e) => e.to === id).forEach((e) => { if (!s.has(e.from)) { s.add(e.from); up(e.from); } });
    const down = (id: number) => tree.edges.filter((e) => e.from === id).forEach((e) => { if (!s.has(e.to)) { s.add(e.to); down(e.to); } });
    up(hover); down(hover);
    return s;
  }, [hover, tree.edges]);

  return (
    <div className="card overflow-x-auto p-2">
      <svg width={width} height={height} role="img" aria-label="Skill tree of prerequisite relationships">
        {tree.edges.map((e, i) => {
          const a = pos.get(e.from), b = pos.get(e.to);
          if (!a || !b) return null;
          const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2, mx = (x1 + x2) / 2;
          const on = related ? related.has(e.from) && related.has(e.to) : false;
          return <path key={i} d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`} fill="none"
            stroke={on ? "#1E2A44" : "#C5CEDC"} strokeWidth={on ? 2.2 : 1.2} opacity={related && !on ? 0.25 : 1} />;
        })}
        {tree.nodes.map((n) => {
          const p = pos.get(n.id)!;
          const dim = related && !related.has(n.id);
          const label = n.title.length > 22 ? n.title.slice(0, 21) + "…" : n.title;
          return (
            <g key={n.id} transform={`translate(${p.x},${p.y})`} opacity={dim ? 0.3 : 1} className="cursor-pointer"
              tabIndex={0} role="link" aria-label={`${n.title}: ${STATUS_LABEL[n.status]}, ${Math.round(n.mastery)}%`}
              onMouseEnter={() => setHover(n.id)} onMouseLeave={() => setHover(null)}
              onFocus={() => setHover(n.id)} onBlur={() => setHover(null)}
              onClick={() => nav(`/topics/${n.id}`)} onKeyDown={(ev) => ev.key === "Enter" && nav(`/topics/${n.id}`)}>
              <title>{`${n.title} — ${STATUS_LABEL[n.status]} (${Math.round(n.mastery)}%)`}</title>
              <rect width={W} height={H} rx={8} fill={FILL[n.status]}
                stroke={n.status === "NEEDS_REVISION" ? "#B83A4B" : n.status === "AVAILABLE" ? "#1E2A44" : "#C5CEDC"}
                strokeWidth={n.status === "AVAILABLE" ? 1.5 : 1} strokeDasharray={n.is_project ? "4 3" : undefined} />
              <rect x={0} y={H - 4} width={(W * Math.min(100, n.mastery)) / 100} height={4} rx={2} fill="#F5D547" opacity={n.mastery > 0 ? 0.9 : 0} />
              <text x={10} y={H / 2 + 4} fontSize={12} fontWeight={700} fill={TEXT[n.status]} fontFamily="Atkinson Hyperlegible, sans-serif">
                {n.status === "LOCKED" ? "🔒 " : ""}{label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
