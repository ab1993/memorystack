#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import logging
import base64
from .. import models, database, notifications

logger = logging.getLogger(__name__)

router = APIRouter()
manager = notifications.manager.NotificationManager()

# --- FIXED: Robust Base64 Decoding ---
def decode_user_id(encoded_str: str):
    try:
        # 1. Add back the correct amount of padding
        # Base64 strings must have a length divisible by 4
        missing_padding = len(encoded_str) % 4
        if missing_padding:
            encoded_str += '=' * (4 - missing_padding)

        # 2. Decode using urlsafe (which handles the '-' and '_' we used in JS)
        decoded_bytes = base64.urlsafe_b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"🔥 Decoding Error: {str(e)}")
        return None

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request, db: Session = Depends(database.get_db)):
    logger.info("🚀 Webhook received!")
    data = await request.json()

    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        logger.debug(f"📩 Incoming Message: '{text}' | Chat ID: {chat_id}")

        if text.startswith("/start"):
            parts = text.split(" ")

            if len(parts) > 1:
                encoded_id = parts[1]

                # 🔓 Decode the masked ID
                internal_user_id = decode_user_id(encoded_id)
                logger.debug(f"🔍 Attempting to link UUID: {internal_user_id}")

                if not internal_user_id:
                    logger.error("❌ Failed to decode Telegram start token")
                    return {"ok": True}

                try:
                    user = db.query(models.User).filter(models.User.id == str(internal_user_id)).first()

                    if user:
                        user.telegram_chat_id = chat_id
                        db.commit()
                        logger.info(f"✅ SUCCESS: Database updated for User {user.email}")

                        # Send confirmation to the user's phone
                        await manager.broadcast_revision(
                            chat_id,
                            "System Sync",
                            type('obj', (object,), {
                                'layer_1_gist': "Success! Your account is linked.",
                                'layer_2_pattern': "You'll now receive revision notes here.",
                                'layer_3_questions': ["Try generating a topic on the web!"]
                            })
                        )
                    else:
                        logger.error(f"❌ ERROR: User UUID {internal_user_id} not found in DB.")
                except Exception as e:
                    logger.error(f"🔥 Database Error during linking: {e}")
            else:
                logger.warning("⚠️ /start received but no ID found.")

    return {"ok": True}