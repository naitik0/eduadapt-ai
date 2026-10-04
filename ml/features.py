"""Shared feature schema for the learner classifier (used by training and serving)."""
GOALS = ["placement", "job_ready", "web_development", "data_science", "fundamentals", "project_building"]
INTERESTS = ["web", "data", "ai", "games", "systems", "mobile", "automation", "security", "cloud"]

FEATURES = [
    "previous_score",      # mean quiz score before the most recent 3 attempts (0-100)
    "recent_score",        # mean of the last 3 quiz scores (0-100)
    "attempts",            # total quiz attempts
    "study_hours",         # planned weekly study hours
    "completion_rate",     # completed topics / started topics (0-1)
    "time_per_question",   # average seconds per quiz question
    "topic_mastery",       # mean mastery over the active roadmap (0-100)
    "goal",                # index into GOALS
    "interest",            # index into INTERESTS (primary interest)
    "difficulty",          # mean difficulty of attempted topics (1-4)
]
TARGETS = ["learning_level", "learning_pace", "support_level"]
