# backend/app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from . import models, database, notifications

# We use the AsyncIOScheduler because sending Telegram messages uses 'await'
scheduler = AsyncIOScheduler()
manager = notifications.manager.NotificationManager()

async def check_and_send_revisions():
    print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] Scheduler woke up! Checking for due revisions...")

    # We create a manual database session because we aren't inside an API route
    db = database.SessionLocal()

    try:
        now = datetime.utcnow()

        # 1. Find all notes where the revision date is right now or in the past
        due_notes = db.query(models.AtomicNote).filter(
            models.AtomicNote.next_revision <= now
        ).all()

        if not due_notes:
            print("📭 No revisions due right now.")
            return

        print(f"📦 Found {len(due_notes)} topics due for revision!")

        # 2. Loop through them and send via Telegram
        for note in due_notes:
            user = db.query(models.User).filter(models.User.id == note.user_id).first()

            if user and user.telegram_chat_id:
                print(f"📤 Auto-pushing '{note.topic}' to User {user.id}")
                await manager.broadcast_revision(user.telegram_chat_id, note.topic, note)

                # SAFETY MEASURE FOR TESTING:
                # Push the date forward by 1 hour so it doesn't spam you every minute
                # while we wait to build the FSRS rating buttons tomorrow.
                note.next_revision = now + timedelta(hours=1)
                db.commit()

    except Exception as e:
        print(f"🔥 Scheduler Error: {e}")
    finally:
        db.close() # Always close the DB connection!

def start_scheduler():
    # For testing, we run this every 1 minute.
    # In production, we will change this to run once a day at 8:00 AM.
    scheduler.add_job(check_and_send_revisions, 'interval', minutes=1)
    scheduler.start()
    print("⏱️ Background Scheduler started and ticking...")