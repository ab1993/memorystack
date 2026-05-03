#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

# backend/app/main.py
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from . import auth
import os
import json
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load env variables before other local imports
load_dotenv()

from app import models, schemas, database, sprint_engine
from .ai_agent import ContentAgent
from .notifications.manager import NotificationManager
from .notifications import discovery
from .scheduler import start_scheduler
from fsrs import FSRS, Card, Rating

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MemoryStack] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# You can now use 'logger.info("message")' anywhere in your code!

# 1. Initialize our Notification Manager early so all endpoints can use it
manager = NotificationManager()

# 2. Define what happens on Startup (Heartbeat)
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

class UserCreate(BaseModel):
    email: str
    password: str

# 3. Initialize FastAPI
app = FastAPI(title="MemoryStack API", lifespan=lifespan)

# Include Routers
app.include_router(discovery.router)

# 4. CORS Middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to get DB
get_db = database.get_db

# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {"message": "MemoryStack API Server is live!"}

@app.get("/topics", response_model=list[schemas.TopicBase])
def get_topics(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    """Fetch ONLY the topics that belong to the logged-in user."""

    # We join the AtomicNote table with the UserRevision table
    # to filter out only the notes this specific user is tracking!
    user_notes = db.query(models.AtomicNote).join(
        models.UserRevision,
        models.AtomicNote.id == models.UserRevision.note_id
    ).filter(
        models.UserRevision.user_id == current_user.id
    ).all()

    return user_notes

@app.post("/generate-sprint", response_model=schemas.SprintResponse)
def create_sprint(request: schemas.SprintRequest, current_user: models.User = Depends(auth.get_current_user)):
    """Generate a custom revision plan based on the deadline."""
    plan = sprint_engine.SprintEngine.generate_plan(
        request.interview_date,
        request.selected_topics
    )
    if "error" in plan:
        raise HTTPException(status_code=400, detail=plan["error"])
    return plan

@app.post("/topics/generate/{topic_name}")
async def generate_topic(topic_name: str, db: Session = Depends(get_db),
                         current_user: models.User = Depends(auth.get_current_user)):
    """Agentically generates content, saves to BOTH tables, and pushes to Telegram."""

    logger.info(f"🤖 Generating content for: {topic_name}")

    # 2. Check if topic already exists in AtomicNotes
    note = db.query(models.AtomicNote).filter(models.AtomicNote.topic == topic_name).first()

    if not note:
        # Generate with AI Agent
        try:
            ai_data = ContentAgent.generate_note(topic_name)

            # Ensure questions are formatted as a string/JSON for the DB
            questions = ai_data.get('layer_3_questions', [])
            if isinstance(questions, str):
                try:
                    questions = json.loads(questions)
                except:
                    questions = [questions]

            # Save to AtomicNote Table
            note = models.AtomicNote(
                topic=ai_data.get('topic', topic_name),
                category=ai_data.get('category', 'System Design'),
                layer_1_gist=ai_data['layer_1_gist'],
                layer_2_pattern=ai_data['layer_2_pattern'],
                layer_3_questions=questions
            )
            db.add(note)
            db.commit()
            db.refresh(note)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

    # 3. Save to UserRevision Table (The FSRS tracking)
    revision = db.query(models.UserRevision).filter(
        models.UserRevision.user_id == current_user.id,
        models.UserRevision.note_id == note.id
    ).first()

    now = datetime.utcnow()
    if not revision:
        revision = models.UserRevision(
            user_id=current_user.id,
            note_id=note.id,
            next_review=now # Due immediately for the first push!
        )
        db.add(revision)
        db.commit()
    else:
        # If they generate it again, force a review now
        revision.next_review = now
        db.commit()

    # 4. THE PUSH: Send to your phone immediately
    if current_user.telegram_chat_id:
        logger.info(f"📤 Pushing {topic_name} to Telegram ID: {current_user.telegram_chat_id}")
        await manager.broadcast_revision(current_user.telegram_chat_id, topic_name, note)
    else:
        logger.info(f"⚠️ Topic generated, but User {current_user.id} has no telegram_chat_id linked.")

    return {"status": "Success", "topic": topic_name, "note_id": note.id}

@app.post("/review/{note_id}")
def review_topic(note_id: str, rating: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    """Update the user's memory state for a topic."""
    from datetime import timedelta

    fsrs_engine = FSRS()
    # 1. Look for existing progress
    revision = db.query(models.UserRevision).filter(
        models.UserRevision.note_id == note_id,
        models.UserRevision.user_id == current_user.id
    ).first()

    now = datetime.now(timezone.utc)

    # 2. IF FIRST TIME REVIEWING: Create a blank card instead of throwing 404!
    if not revision:
        logger.info(f"🌱 First time reviewing Note {note_id}. Creating tracker...")
        revision = models.UserRevision(
            user_id=current_user.id,
            note_id=note_id,
            next_review=now.replace(tzinfo=None)
        )
        db.add(revision)
        db.commit()
        db.refresh(revision)
        card = Card() # Start with a brand new FSRS memory card
    else:
        # Load existing memory card state
        card = Card()
        card.stability = revision.stability
        card.difficulty = revision.difficulty
        card.elapsed_days = revision.elapsed_days
        card.scheduled_days = revision.scheduled_days
        card.reps = revision.reps
        card.state = revision.state
        card.last_review = revision.last_review.replace(tzinfo=timezone.utc)

    # 3. Process the Rating
    fsrs_rating = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}.get(rating, Rating.Good)

    scheduling_cards = fsrs_engine.repeat(card, now)
    updated_card = scheduling_cards[fsrs_rating].card

    # 4. Save updated memory state back to DB
    revision.stability = updated_card.stability
    revision.difficulty = updated_card.difficulty
    revision.elapsed_days = updated_card.elapsed_days
    revision.scheduled_days = updated_card.scheduled_days
    revision.reps = updated_card.reps
    revision.state = updated_card.state
    revision.last_review = now

    # Calculate exactly when this needs to be pushed to Telegram next
    revision.next_review = now.replace(tzinfo=None) + timedelta(days=updated_card.scheduled_days)

    db.commit()
    return {"next_review_days": updated_card.scheduled_days, "status": "Success"}

@app.get("/user/status")
def get_user_status(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "telegram_chat_id": current_user.telegram_chat_id
    }


# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user with a hashed password."""
    # 1. Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Hash the password and save the user
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully!", "user_id": new_user.id}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Checks credentials and returns a JWT token."""
    # Note: OAuth2 uses "username" by default, so we pass the email into the username field
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    # 1. Verify user exists and password is correct
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # 2. Generate the secure token
    access_token = auth.create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }