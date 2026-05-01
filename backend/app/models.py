from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from .database import Base
from datetime import datetime
import uuid

class AtomicNote(Base):
    __tablename__ = "atomic_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    topic = Column(String, index=True)  # e.g., "Sliding Window"
    category = Column(String)           # e.g., "DS", "System Design"

    # The 3-Layer Hierarchy
    layer_1_gist = Column(Text)         # 3-sentence summary
    layer_2_pattern = Column(Text)      # When to use + Logic
    layer_3_questions = Column(JSON)    # List of high-freq questions (JSON array)

    created_at = Column(DateTime, default=datetime.utcnow)

class UserRevision(Base):
    __tablename__ = "user_revisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"))
    note_id = Column(String, ForeignKey("atomic_notes.id"))

    # FSRS Memory Fields (The AI Brain for scheduling)
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)
    elapsed_days = Column(Integer, default=0)
    scheduled_days = Column(Integer, default=0)
    reps = Column(Integer, default=0)
    state = Column(Integer, default=0) # 0=New, 1=Learning, 2=Review
    last_review = Column(DateTime, default=datetime.utcnow)
    next_review = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    telegram_chat_id = Column(String, nullable=True)