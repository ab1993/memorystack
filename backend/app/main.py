from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database, sprint_engine
from .ai_agent import ContentAgent
from fsrs import FSRS, Card, Rating
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # 1. Import Middleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
load_dotenv() # This must be called BEFORE you initialize the NotificationManager
from .notifications.manager import NotificationManager
from sqlalchemy.orm import Session
from . import models, database, fsrs # Ensure these are imported
# 👇 IMPORT OUR NEW SCHEDULER
from .scheduler import start_scheduler
from contextlib import asynccontextmanager

# 👇 DEFINE WHAT HAPPENS ON STARTUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    start_scheduler()
    yield
    # Anything here runs when the server shuts down

app = FastAPI(title="MemoryStack API",lifespan=lifespan)
from .notifications import discovery

app.include_router(discovery.router)

# 2. Define the "Trusted" origins
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 3. Add the middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to get DB
get_db = database.get_db

@app.get("/")
def read_root():
    return {"message": "MemoryStack API is live!"}

@app.get("/topics", response_model=List[schemas.TopicBase])
def get_topics(db: Session = Depends(get_db)):
    """Fetch all available DS & System Design topics."""
    return db.query(models.AtomicNote).all()

@app.post("/generate-sprint", response_model=schemas.SprintResponse)
def create_sprint(request: schemas.SprintRequest):
    """Generate a custom revision plan based on the deadline."""
    plan = sprint_engine.SprintEngine.generate_plan(
        request.interview_date,
        request.selected_topics
    )

    if "error" in plan:
        raise HTTPException(status_code=400, detail=plan["error"])

    return plan


@app.post("/topics/generate/{topic_name}")
def generate_new_topic(topic_name: str, db: Session = Depends(get_db)):
    """Agentically generates and saves a new topic note using GPT-4o."""

    # 1. Check if it already exists
    existing = db.query(models.AtomicNote).filter(models.AtomicNote.topic == topic_name).first()
    if existing:
        return {"message": "Topic already exists", "data": existing}

    # 2. Use Agent to generate content
    try:
        ai_data = ContentAgent.generate_note(topic_name)

        questions = ai_data.get('layer_3_questions', [])
        # Force conversion to list if AI returned a string
        if isinstance(questions, str):
            try:
                questions = json.loads(questions)
            except:
                questions = [questions]

        # 3. Save to DB
        new_note = models.AtomicNote(
            topic=ai_data['topic'],
            category=ai_data['category'],
            layer_1_gist=ai_data['layer_1_gist'],
            layer_2_pattern=ai_data['layer_2_pattern'],
            layer_3_questions=ai_data['layer_3_questions']
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        return new_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/topics/generate")
async def generate_topic(topic_name: str, db: Session = Depends(database.get_db)):
    # 1. Look up our linked user (Hardcoded to 1 for Beta)
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user or not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram not linked!")

    print(f"🤖 Generating content for: {topic_name}")

    # 2. MOCK AI GENERATION (Replace this with your actual LLM call later)
    # This ensures the pipe works even if your OpenAI API isn't ready
    ai_note = {
        "gist": f"{topic_name} is a vital pattern in system design used for scaling.",
        "pattern": "Implementation involves a distributed hash table and nodes on a circular ring.",
        "challenges": ["How do you handle node hotspots?", "What happens during cascading failures?"]
    }

    # 3. Save to Database
    new_note = models.AtomicNote(
        user_id=1,
        topic=topic_name,
        layer_1_gist=ai_note["gist"],
        layer_2_pattern=ai_note["pattern"],
        layer_3_questions=str(ai_note["challenges"]), # Store as string/JSON
        next_revision=datetime.utcnow(),
        stability=0.1
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    # 4. THE PUSH: Send to your phone immediately
    print(f"📤 Pushing {topic_name} to Telegram ID: {user.telegram_chat_id}")
    await manager.broadcast_revision(
        user.telegram_chat_id,
        topic_name,
        new_note # This passes the object to your Telegram strategy
    )

    return {"status": "Success", "topic": topic_name}


@app.post("/review/{note_id}")
def review_topic(note_id: int, rating: int, db: Session = Depends(database.get_db)):
    """
    Update the user's memory state for a topic.
    rating: 1 (Again), 2 (Hard), 3 (Good), 4 (Easy)
    """

    fsrs_engine = FSRS()
    revision = db.query(models.UserRevision).filter(models.UserRevision.note_id == note_id).first()

    if not revision:
        card = Card()
        revision = models.UserRevision(user_id="default_user", note_id=note_id)
    else:
        # Load existing card state
        card = Card()
        card.stability = revision.stability
        card.difficulty = revision.difficulty
        card.elapsed_days = revision.elapsed_days
        card.scheduled_days = revision.scheduled_days
        card.reps = revision.reps
        card.state = revision.state
        card.last_review = revision.last_review.replace(tzinfo=timezone.utc)

    # 1. Map user rating to FSRS Rating
    fsrs_rating = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}.get(rating, Rating.Good)

    now = datetime.now(timezone.utc)

    # 2. FIX: In version 3.1.0, we use .repeat()
    # This returns a dictionary of potential 'SchedulingCards'
    scheduling_cards = fsrs_engine.repeat(card, now)

    # 3. Extract the specific 'card' and 'review_log' for the chosen rating
    chosen_scheduling_card = scheduling_cards[fsrs_rating]
    updated_card = chosen_scheduling_card.card
    # chosen_scheduling_card.review_log can be used if you want to track history later

    # 4. Save updated card back to DB
    revision.stability = updated_card.stability
    revision.difficulty = updated_card.difficulty
    revision.elapsed_days = updated_card.elapsed_days
    revision.scheduled_days = updated_card.scheduled_days
    revision.reps = updated_card.reps
    revision.state = updated_card.state
    revision.last_review = now

    if not db.query(models.UserRevision).filter(models.UserRevision.note_id == note_id).first():
        db.add(revision)

    db.commit()
    return {"next_review_days": updated_card.scheduled_days}

# Initialize the manager
notification_manager = NotificationManager()

@app.post("/test-notification")
async def test_notification():
    # This pulls your ID from the .env file we created
    test_chat_id = os.getenv("TEST_TELEGRAM_CHAT_ID")

    if not test_chat_id:
        raise HTTPException(status_code=400, detail="TEST_TELEGRAM_CHAT_ID not found in .env")

    # Dummy data to simulate a real note
    sample_note = type('obj', (object,), {
        'layer_1_gist': "A Trie (Prefix Tree) is a tree-like data structure used for efficient retrieval of keys in a dataset of strings.",
        'layer_2_pattern': "Use it when dealing with prefix matching, autocomplete, or spell checkers. Logic: Each node represents a character.",
        'layer_3_questions': [
            "Implement Trie (Prefix Tree)",
            "Word Search II",
            "Design Add and Search Words Data Structure"
        ]
    })

    try:
        await notification_manager.broadcast_revision(
            recipient_id=test_chat_id,
            topic="Trie (Test)",
            note_data=sample_note
        )
        return {"status": "success", "message": "Check your Telegram!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/user/{user_id}/status")
def get_user_status(user_id: int, db: Session = Depends(database.get_db)):
    # Look up the user in the database
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return {"telegram_chat_id": None, "error": "User not found"}

    return {
        "user_id": user.id,
        "telegram_chat_id": user.telegram_chat_id # This will be null until they hit Start
    }