from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TopicBase(BaseModel):
    id: int
    topic: str
    category: str


    class Config:
        from_attributes = True

class SprintRequest(BaseModel):
    interview_date: str  # YYYY-MM-DD
    selected_topics: List[str]

class SprintResponse(BaseModel):
    metadata: Dict[str, Any]
    schedule: Dict[str, Any]