from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import logging
from .. import models, database, notifications

# --- NEW: Logging Configuration ---
logger = logging.getLogger(__name__)

router = APIRouter()
manager = notifications.manager.NotificationManager()

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request, db: Session = Depends(database.get_db)):
    logger.info("🚀 Webhook received!")
    data = await request.json()

    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        logger.info(f"📩 Incoming Message: '{text}' | Chat ID: {chat_id}")

        if text.startswith("/start"):
            parts = text.split(" ")

            if len(parts) > 1:
                internal_user_id = parts[1]
                logger.info(f"🔍 Attempting to link UUID: {internal_user_id}")

                try:
                    # ✅ FIXED: Removed int() cast. UUIDs are strings!
                    user = db.query(models.User).filter(models.User.id == str(internal_user_id)).first()

                    if user:
                        user.telegram_chat_id = chat_id
                        db.commit()
                        logger.info(f"✅ SUCCESS: Database updated for User {user.email}")

                        # Send a "Linked" confirmation immediately!
                        logger.info("📤 Sending Telegram confirmation...")
                        await manager.broadcast_revision(
                            chat_id,
                            "System Sync",
                            type('obj', (object,), {
                                'layer_1_gist': "Your account is now linked to MemoryStack!",
                                'layer_2_pattern': "You will receive revision notes here based on your sprint schedule.",
                                'layer_3_questions': ["Try generating a sprint on the web dashboard!"]
                            })
                        )
                    else:
                        logger.error(f"❌ ERROR: User UUID {internal_user_id} not found in DB.")
                except Exception as e:
                    logger.error(f"🔥 Database Error during linking: {e}")
            else:
                logger.warning("⚠️ /start received but no ID parameter found.")

    return {"ok": True}