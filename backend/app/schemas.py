from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TopicBase(BaseModel):
    id: str
    topic: str
    category: str
    layer_1_gist: Optional[str] = None
    layer_2_pattern: Optional[str] = None
    layer_3_questions: Optional[List[str]] = []

    class Config:
        from_attributes = True

class SprintRequest(BaseModel):
    interview_date: str  # YYYY-MM-DD
    selected_topics: List[str]

# 👇 NEW: Defines exactly what a single day's task looks like
class SprintTask(BaseModel):
    day: str
    topic: str
    focus: str
    status: str

class SprintResponse(BaseModel):
    target_date: str
    metadata: Dict[str, Any]
    sprint_plan: List[SprintTask]