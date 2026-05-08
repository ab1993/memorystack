#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

# backend/app/notifications/telegram_provider.py
import httpx
import os
from .base import NotificationProvider
import logging
from ..security import decrypt_chat_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MemoryStack] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class TelegramProvider(NotificationProvider):
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_revision(self, recipient_id: str, topic: str, content: dict):
        message = (
                f"🧠 *MemoryStack Revision: {topic}*\n\n"
                f"📍 *Layer 1 (The Gist):*\n{content['l1']}\n\n"
                f"⚙️ *Layer 2 (The Pattern):*\n{content['l2']}\n\n"
                f"❓ *Challenges:*\n" +
                "\n".join([f"• {q}" for q in content['l3']])
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": decrypt_chat_id(recipient_id),
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )

            # DEBUG LOGS: Check your terminal after running the test!
            logger.debug(f"Telegram Request to ID: {recipient_id}")
            logger.info(f"Status Code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Telegram Error Details: {response.text}")

            return response.status_code == 200