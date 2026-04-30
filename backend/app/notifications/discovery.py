from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from .. import models, database, notifications

router = APIRouter()
manager = notifications.manager.NotificationManager()

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request, db: Session = Depends(database.get_db)):
    print("🚀 Webhook received!")
    data = await request.json()

    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        # DEBUG: Let's see what Telegram is actually sending
        print(f"📩 Raw Text: '{text}' | Chat ID: {chat_id}")

        if text.startswith("/start"):
            parts = text.split(" ")

            if len(parts) > 1:
                internal_user_id = parts[1]
                print(f"🔍 Attempting to link User ID: {internal_user_id}")

                try:
                    # Link the chat_id to our local user
                    user = db.query(models.User).filter(models.User.id == int(internal_user_id)).first()

                    if user:
                        user.telegram_chat_id = chat_id
                        db.commit()
                        print(f"✅ SUCCESS: Database updated for User {internal_user_id}")

                        # Send a "Linked" confirmation immediately!
                        print("📤 Sending Telegram confirmation...")
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
                        print(f"❌ ERROR: User ID {internal_user_id} not found in DB.")
                except Exception as e:
                    print(f"🔥 DB/Broadcast Error: {e}")
            else:
                print("⚠️ WARNING: /start received but no ID parameter found. (Did you type it manually?)")

    return {"ok": True}