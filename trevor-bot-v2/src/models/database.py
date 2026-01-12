"""Database models for Trevor Bot."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from src.config import settings

Base = declarative_base()


class User(Base):
    """User model for patient accounts."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Platform identifiers
    telegram_id = Column(String, unique=True, nullable=True, index=True)
    whatsapp_number = Column(String, unique=True, nullable=True, index=True)
    messenger_id = Column(String, unique=True, nullable=True, index=True)

    # User information
    email = Column(String, unique=True, nullable=True, index=True)
    username = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=True)

    # Authentication
    password_hash = Column(String, nullable=True)

    # FHIR reference
    fhir_patient_id = Column(String, unique=True, nullable=True, index=True)

    # Preferences
    language = Column(String, default="fr")
    timezone = Column(String, default="Europe/Zurich")
    notifications_enabled = Column(Boolean, default=True)

    # Privacy & Community
    peer_matching_enabled = Column(Boolean, default=False)
    anonymous_profile = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    observations = relationship("Observation", back_populates="user")
    coaching_plans = relationship("CoachingPlan", back_populates="user")


class Conversation(Base):
    """Conversation history for context and analytics."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Message content
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    platform = Column(String, nullable=False)  # telegram, whatsapp, messenger

    # Metadata
    intent = Column(String, nullable=True)  # symptom_report, appointment, question, etc.
    confidence = Column(Float, nullable=True)

    # Context
    fhir_reference = Column(String, nullable=True)  # Link to FHIR resource if created

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")


class Observation(Base):
    """Health observations (symptoms, vitals, questionnaire responses)."""

    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Observation details
    observation_type = Column(String, nullable=False)  # symptom, vital, questionnaire
    category = Column(String, nullable=True)  # pain, fatigue, hydration, etc.
    value = Column(JSON, nullable=False)  # Flexible JSON for different types

    # Severity/Score
    severity = Column(String, nullable=True)  # mild, moderate, severe
    score = Column(Float, nullable=True)

    # FHIR reference
    fhir_observation_id = Column(String, unique=True, nullable=True)

    # Timestamps
    observed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="observations")


class CoachingPlan(Base):
    """Personalized coaching plans and recommendations."""

    __tablename__ = "coaching_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Plan details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    goals = Column(JSON, nullable=False)  # List of goals

    # Status
    status = Column(String, default="active")  # active, completed, cancelled
    progress = Column(Float, default=0.0)  # 0-100

    # FHIR reference
    fhir_careplan_id = Column(String, unique=True, nullable=True)

    # Timestamps
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="coaching_plans")
    recommendations = relationship("Recommendation", back_populates="coaching_plan")


class Recommendation(Base):
    """Individual coaching recommendations."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    coaching_plan_id = Column(Integer, ForeignKey("coaching_plans.id"), nullable=False)

    # Recommendation details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # hydration, medication, activity, etc.

    # Status
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    coaching_plan = relationship("CoachingPlan", back_populates="recommendations")


class AppointmentRequest(Base):
    """HUG@Home appointment requests."""

    __tablename__ = "appointment_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Request details
    reason = Column(Text, nullable=False)
    urgency = Column(String, nullable=False)  # routine, urgent, very_urgent
    preferred_times = Column(JSON, nullable=True)  # List of datetime options

    # Status
    status = Column(String, default="pending")  # pending, scheduled, completed, cancelled

    # Communication
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)

    # FHIR reference
    fhir_communication_request_id = Column(String, unique=True, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeSource(Base):
    """Curated medical knowledge sources for RAG."""

    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, index=True)

    # Source information
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # guideline, study, patient_experience
    url = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Metadata
    category = Column(String, nullable=True)  # crisis_management, prevention, etc.
    language = Column(String, default="fr")
    reliability_score = Column(Float, default=1.0)  # 0-1

    # Vector embedding
    embedding_id = Column(String, unique=True, nullable=True)  # ChromaDB ID

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
