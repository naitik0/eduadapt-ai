import type { Status } from "../api/types";

export const GOAL_LABEL: Record<string, string> = {
  placement: "Placement and interviews", job_ready: "Job-ready skills", web_development: "Web development",
  data_science: "Data science", fundamentals: "Strong fundamentals", project_building: "Building projects",
};

export const INTEREST_LABEL: Record<string, string> = {
  web: "Web", data: "Data", ai: "AI", games: "Games", systems: "Systems", mobile: "Mobile",
  automation: "Automation", security: "Security", cloud: "Cloud",
};

export const PREFERENCE_LABEL: Record<string, string> = {
  reading: "Reading notes and docs", visual: "Watching videos and diagrams", hands_on: "Hands-on practice",
};

export const STATUS_LABEL: Record<Status, string> = {
  LOCKED: "Locked", AVAILABLE: "Available", IN_PROGRESS: "In progress", COMPLETED: "Completed",
  NEEDS_REVISION: "Needs revision", MASTERED: "Mastered",
};

export const STATUS_STYLE: Record<Status, string> = {
  LOCKED: "bg-grid text-ink-faint border-rule",
  AVAILABLE: "bg-white text-ink border-ink/30",
  IN_PROGRESS: "bg-progress-soft text-progress border-progress/30",
  COMPLETED: "bg-mastery-soft text-mastery border-mastery/30",
  NEEDS_REVISION: "bg-revise-soft text-revise border-revise/30",
  MASTERED: "bg-mastery text-white border-mastery",
};

export const COMPONENT_LABEL: Record<string, string> = {
  knowledge_gap: "Knowledge gap", goal_relevance: "Goal relevance", prerequisite_priority: "Prerequisite priority",
  recent_performance: "Recent performance", interest_match: "Interest match", difficulty_fit: "Difficulty fit",
  feedback: "Your feedback",
};

export const ACTIVITY_LABEL: Record<string, string> = {
  learn: "Learn", examples: "Work through examples", practice: "Practice", quiz: "Quiz", review: "Review mistakes",
  project: "Project work",
};

export function minutes(m: number) {
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60), r = m % 60;
  return r ? `${h} h ${r} min` : `${h} h`;
}

export function shortDate(iso: string) {
  return new Date(iso + (iso.length === 10 ? "T00:00:00" : "")).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
