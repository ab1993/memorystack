#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

from abc import ABC, abstractmethod

class NotificationProvider(ABC):
    @abstractmethod
    async def send_revision(self, recipient_id: str, topic: str, content: dict):
        """
         Standardized method for all providers.
         recipient_id: The unique ID for the service (chat_id, email, etc.)
         content: {'l1': str, 'l2': str, 'l3': list}
         """
        pass