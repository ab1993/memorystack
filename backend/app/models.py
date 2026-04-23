from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from .database import Base
from datetime import datetime

class AtomicNote(Base):
    __tablename__ = "atomic_notes"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)  # e.g., "Sliding Window"
    category = Column(String)           # e.g., "DS", "System Design"

    # The 3-Layer Hierarchy
    layer_1_gist = Column(Text)         # 3-sentence summary
    layer_2_pattern = Column(Text)      # When to use + Logic
    layer_3_questions = Column(JSON)    # List of high-freq questions (JSON array)

    created_at = Column(DateTime, default=datetime.utcnow)

class UserRevision(Base):
    __tablename__ = "user_revisions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # For now, can be a simple string/email
    note_id = Column(Integer, ForeignKey("atomic_notes.id"))

    # FSRS Memory Fields (The AI Brain for scheduling)
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)
    elapsed_days = Column(Integer, default=0)
    scheduled_days = Column(Integer, default=0)
    reps = Column(Integer, default=0)
    state = Column(Integer, default=0) # 0=New, 1=Learning, 2=Review

    last_review = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # NEW: Store the discovered chat_id here
    telegram_chat_id = Column(String, nullable=True)