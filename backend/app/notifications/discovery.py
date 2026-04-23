from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from .. import models, database, notifications

router = APIRouter()
manager = notifications.manager.NotificationManager()

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()

    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        # Catch the /start command with the user_id payload
        if text.startswith("/start"):
            # Example: "/start 1"
            parts = text.split(" ")
            if len(parts) > 1:
                internal_user_id = parts[1]

                # Link the chat_id to our local user
                user = db.query(models.User).filter(models.User.id == int(internal_user_id)).first()
                if user:
                    user.telegram_chat_id = chat_id
                    db.commit()

                    # Send a "Linked" confirmation immediately!
                    await manager.broadcast_revision(
                        chat_id,
                        "System Sync",
                        type('obj', (object,), {
                            'layer_1_gist': "Your account is now linked to MemoryStack!",
                            'layer_2_pattern': "You will receive revision notes here based on your sprint schedule.",
                            'layer_3_questions': ["Try generating a sprint on the web dashboard!"]
                        })
                    )
    return {"ok": True}