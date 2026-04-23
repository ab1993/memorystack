# backend/app/notifications/manager.py
from .telegram_provider import TelegramProvider

class NotificationManager:
    def __init__(self):
        # Tomorrow, you can just add EmailProvider() or WhatsAppProvider() here
        self.providers = [TelegramProvider()]

    async def broadcast_revision(self, recipient_id: str, topic: str, note_data: any):
        content = {
            "l1": note_data.layer_1_gist,
            "l2": note_data.layer_2_pattern,
            "l3": note_data.layer_3_questions
        }

        # Send via all active channels
        for provider in self.providers:
            await provider.send_revision(recipient_id, topic, content)