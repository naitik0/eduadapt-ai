export type Status = "LOCKED" | "AVAILABLE" | "IN_PROGRESS" | "COMPLETED" | "NEEDS_REVISION" | "MASTERED";

export interface User { id: number; name: string; email: string; role: "student" | "admin"; onboarded: boolean }

export interface Profile {
  id: number; name: string; email: string; role: string; goal: string | null; interests: string[];
  daily_minutes: number; target_date: string | null; learning_preference: string;
  learning_level: string; learning_pace: string; support_level: string; classification_confidence: number;
  classification_features: Record<string, number>; streak_days: number; onboarded: boolean;
  options: { goals: string[]; interests: string[] };
}

export interface Skill { slug: string; name: string; category: string; description: string; topics: number }

export interface RoadmapSummary {
  skill: string; skill_name: string; title: string; category: string; description: string; total_topics: number;
  levels: { name: string; count: number; sample: string[] }[];
}

export interface TopicNode {
  id: number; slug: string; title: string; difficulty: number; est_minutes: number; is_project: boolean;
  concepts: string[]; status: Status; mastery: number; prerequisites: { id: number; title: string; min_mastery: number }[];
}

export interface RoadmapView {
  roadmap_id: number; skill: string; skill_name: string; title: string; description: string;
  levels: { name: string; order: number; topics: TopicNode[] }[];
  status_counts: Partial<Record<Status, number>>; total_topics: number; completion: number; avg_mastery: number;
  skill_tree?: { skill: string; nodes: TreeNode[]; edges: { from: number; to: number; min_mastery: number }[] };
  assessment_done?: boolean; is_active?: boolean;
}

export interface TreeNode { id: number; title: string; level: string; depth: number; is_project: boolean; status: Status; mastery: number }

export interface MyRoadmap {
  skill: string; skill_name: string; is_active: boolean; assessment_done: boolean; initial_score: number | null;
  completion: number; avg_mastery: number;
}

export interface Recommendation {
  id: number; rank: number; topic_id: number; title: string; level: string; status: Status; mastery: number;
  score: number; reason: string; difficulty: string; est_minutes: number;
  components: Record<string, number>; contributions: Record<string, number>; unlocks: number; created_at: string;
}

export interface Resource {
  id: number; kind: string; title: string; url: string; content: string; difficulty: number; est_minutes: number;
  format: string; match_score: number; why: string;
}

export interface ProjectInfo {
  id: number; topic_id: number; name: string; difficulty: string; est_hours: number; required_skills: string[];
  requirements: string[]; evaluation_criteria: string[];
  milestones: { order: number; title: string; description: string }[];
}

export interface TopicDetail {
  id: number; title: string; skill: string; skill_name: string; level: string; description: string;
  objectives: string[]; concepts: string[]; est_minutes: number; is_project: boolean;
  progress: { mastery: number; status: Status; attempts: number; practice_done: number; last_score: number | null; learned: boolean };
  adaptive: { difficulty: string; level: string; support: string; approach: string };
  prerequisites: { id: number; title: string; min_mastery: number; mastery: number; met: boolean }[];
  unlocks: { id: number; title: string }[];
  resources: Resource[]; practice: string[]; project: ProjectInfo | null;
}

export interface LoopResult {
  event: string; pipeline?: string[];
  mastery_change?: { topic_id: number; topic: string; before: number; after: number } | null;
  status_changes?: { topic_id: number; topic: string; from: Status; to: Status }[];
  unlocked?: string[];
  classification?: { learning_level: string; learning_pace: string; support_level: string; confidence: number; source: string };
  classification_changed?: boolean; previous_recommendation?: string | null;
  recommendation?: Recommendation | null; recommendation_changed?: boolean;
}

export interface QuizQuestion { id: number; question: string; options: string[]; concept: string }
export interface Quiz { quiz_id: number; kind: "diagnostic" | "topic"; difficulty: number; difficulty_label: string; topic_id: number | null; topic: string | null; questions: QuizQuestion[] }
export interface QuizResult {
  correct: number; total: number; score: number; weak_concepts: string[];
  results: { question_id: number; topic_id: number; correct: boolean; chosen: number | null; answer_index: number; explanation: string; concept: string }[];
  placement?: { overall: number; level_accuracy: Record<string, number> };
  loop: LoopResult;
}

export interface PlanItem { id: number; topic_id: number; topic: string; activity: string; minutes: number; done: boolean }
export interface PlanDay { day: number; date: string; total_minutes: number; items: PlanItem[] }
export interface StudyPlan {
  id: number; start_date: string; daily_minutes: number;
  summary: { remaining_minutes: number; days_to_complete: number; estimated_completion: string; topics_scheduled: number; on_track?: boolean | null; minutes_per_day_needed?: number | null; target_date?: string | null };
  today: PlanDay; week: PlanDay[];
}

export interface Analytics {
  profile: { name: string; learning_level: string; learning_pace: string; support_level: string; confidence: number; goal: string; streak_days: number; daily_minutes: number };
  active_skill: string | null; overall_progress: number; avg_mastery: number; topics_total: number; topics_done: number;
  status_counts: Partial<Record<Status, number>>;
  mastery_by_topic: { topic_id: number; title: string; level: string; mastery: number; status: Status; attempts: number; last_score: number | null }[];
  level_performance: { level: string; avg_mastery: number }[];
  skill_mastery: { skill: string; avg_mastery: number; completion: number }[];
  roadmaps: (MyRoadmap & { status_counts: Partial<Record<Status, number>> })[];
  quiz_performance: { id: number; date: string; score: number; kind: string; topic: string }[];
  quiz_avg: number | null; trend: { date: string; avg_score: number | null; topics_completed: number; activity: number }[];
  weak_areas: { topic_id: number; title: string; mastery: number; status: Status }[];
  weak_concepts: { concept: string; count: number }[];
}

export interface ChatSource { source: string; score: number; kind: string }
export interface ChatReply { session_id: number; answer: string; mode: string; context: Record<string, unknown>; sources: ChatSource[] }
