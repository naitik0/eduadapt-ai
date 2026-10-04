"""All persistent entities. JSON columns hold small lists/dicts."""
from datetime import date, datetime, timezone

from sqlalchemy import (JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    goal: Mapped[str] = mapped_column(String(40), default="fundamentals")
    interests: Mapped[list] = mapped_column(JSON, default=list)
    daily_minutes: Mapped[int] = mapped_column(Integer, default=60)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    learning_preference: Mapped[str] = mapped_column(String(20), default="reading")
    learning_level: Mapped[str] = mapped_column(String(20), default="Beginner")
    learning_pace: Mapped[str] = mapped_column(String(20), default="Moderate")
    support_level: Mapped[str] = mapped_column(String(20), default="Medium")
    classification_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    classification_features: Mapped[dict] = mapped_column(JSON, default=dict)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[User] = relationship(back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    docs_url: Mapped[str] = mapped_column(String(255), default="")


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    skill: Mapped[Skill] = relationship()
    levels: Mapped[list["RoadmapLevel"]] = relationship(order_by="RoadmapLevel.order", cascade="all, delete-orphan")


class RoadmapLevel(Base):
    __tablename__ = "roadmap_levels"
    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(40))
    order: Mapped[int] = mapped_column(Integer)


class RoadmapTopic(Base):
    __tablename__ = "roadmap_topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("roadmap_levels.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    concepts: Mapped[list] = mapped_column(JSON, default=list)
    objectives: Mapped[list] = mapped_column(JSON, default=list)
    est_minutes: Mapped[int] = mapped_column(Integer, default=45)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)   # 1 beginner .. 4 projects
    order: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    is_project: Mapped[bool] = mapped_column(Boolean, default=False)
    level: Mapped[RoadmapLevel] = relationship()
    __table_args__ = (UniqueConstraint("roadmap_id", "slug"),)


class TopicPrerequisite(Base):
    __tablename__ = "topic_prerequisites"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), index=True)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"))
    min_mastery: Mapped[float] = mapped_column(Float, default=60)


class StudentRoadmap(Base):
    __tablename__ = "student_roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    assessment_done: Mapped[bool] = mapped_column(Boolean, default=False)
    initial_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    roadmap: Mapped[Roadmap] = relationship()
    __table_args__ = (UniqueConstraint("user_id", "roadmap_id"),)


class StudentTopicProgress(Base):
    __tablename__ = "student_topic_progress"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), index=True)
    mastery: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="LOCKED")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    practice_done: Mapped[int] = mapped_column(Integer, default=0)
    last_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    started: Mapped[bool] = mapped_column(Boolean, default=False)
    learned: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    __table_args__ = (UniqueConstraint("user_id", "topic_id"),)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    difficulty: Mapped[str] = mapped_column(String(20))
    est_hours: Mapped[int] = mapped_column(Integer)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    evaluation_criteria: Mapped[list] = mapped_column(JSON, default=list)
    milestones: Mapped[list["ProjectMilestone"]] = relationship(order_by="ProjectMilestone.order", cascade="all, delete-orphan")


class ProjectMilestone(Base):
    __tablename__ = "project_milestones"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))   # notes|video|practice|documentation|quiz|project
    title: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(400), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    est_minutes: Mapped[int] = mapped_column(Integer, default=15)
    format: Mapped[str] = mapped_column(String(20), default="reading")  # reading|visual|hands_on


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=True)
    kind: Mapped[str] = mapped_column(String(20))   # diagnostic | topic
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    questions: Mapped[list["QuizQuestion"]] = relationship(order_by="QuizQuestion.id", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    answer_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text, default="")
    concept: Mapped[str] = mapped_column(String(120), default="")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=True)
    kind: Mapped[str] = mapped_column(String(20), default="topic")
    score: Mapped[float] = mapped_column(Float)
    correct: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    weak_concepts: Mapped[list] = mapped_column(JSON, default=list)
    time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"))
    rank: Mapped[int] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float)
    components: Mapped[dict] = mapped_column(JSON)
    reason: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(20))
    est_minutes: Mapped[int] = mapped_column(Integer)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recommendation_id: Mapped[int | None] = mapped_column(ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)   # +1 helpful / -1 not helpful
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class StudyPlan(Base):
    __tablename__ = "study_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    start_date: Mapped[date] = mapped_column(Date)
    daily_minutes: Mapped[int] = mapped_column(Integer)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    items: Mapped[list["StudyPlanItem"]] = relationship(
        order_by="(StudyPlanItem.day, StudyPlanItem.order)", cascade="all, delete-orphan")


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("study_plans.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"))
    day: Mapped[int] = mapped_column(Integer)      # 0 = today
    order: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(20))   # learn|examples|practice|quiz|review|project
    minutes: Mapped[int] = mapped_column(Integer)
    done: Mapped[bool] = mapped_column(Boolean, default=False)


class LearningEvent(Base):
    __tablename__ = "learning_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_topics.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    messages: Mapped[list["ChatMessage"]] = relationship(order_by="ChatMessage.id", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class AppSetting(Base):
    """Runtime-tunable settings (e.g. recommendation weights)."""
    __tablename__ = "app_settings"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON)
