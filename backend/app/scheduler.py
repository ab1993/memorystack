#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

# backend/app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

from rich.jupyter import print
from . import models, database, notifications
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MemoryStack] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# We use the AsyncIOScheduler because sending Telegram messages uses 'await'
scheduler = AsyncIOScheduler()
manager = notifications.manager.NotificationManager()

async def check_and_send_revisions():
    logger.info(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] Scheduler woke up! Checking UserRevisions...")

    db = database.SessionLocal()

    try:
        now = datetime.utcnow()

        # 1. Find all due revisions, and fetch the User and the Note at the same time
        due_revisions = db.query(models.UserRevision, models.AtomicNote, models.User). \
            join(models.AtomicNote, models.UserRevision.note_id == models.AtomicNote.id). \
            join(models.User, models.UserRevision.user_id == models.User.id). \
            filter(models.UserRevision.next_review <= now).all()

        if not due_revisions:
            logger.info("📭 No revisions due right now.")
            return

        logger.info(f"Found {len(due_revisions)} topics due for revision!")

        # 2. Loop through and send
        for revision, note, user in due_revisions:
            if user.telegram_chat_id:
                logger.info(f"Auto-pushing '{note.topic}' to User {user.id} (Telegram: {user.telegram_chat_id})")

                # Send to telegram
                await manager.broadcast_revision(user.telegram_chat_id, note.topic, note)

                # Push the date forward by 1 hour for testing
                revision.next_review = now + timedelta(hours=60)
                db.commit()
            else:
                logger.info("Not sent telegram_chat_id is missing, please sync the telegram from memorystack dashboard")

    except Exception as e:
        logger.error(f"🔥 Scheduler Error: {e}")
    finally:
        db.close()

def start_scheduler():
    # For testing, we run this every 1 minute.
    # In production, we will change this to run once a day at 8:00 AM.
    scheduler.add_job(check_and_send_revisions, 'interval', minutes=1)
    scheduler.start()
    logger.info("⏱️ Background Scheduler started and ticking...")