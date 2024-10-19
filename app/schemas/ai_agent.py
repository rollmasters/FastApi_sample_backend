from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

from app.utils.object_id_pydantic_annotation import PyObjectId


class AIResponse(BaseModel):
    question: str
    answer: str
    voice: Optional[str] = Field(alias='voice_answer')  # Corresponds to 'voice_answer' in JSON
    links: Optional[List[str]]
    process_time: Optional[float] = None  # Represented in seconds

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )



class MessageDetail(BaseModel):
    userId: str
    question: str
    answer: str
    time: datetime

class AISummary(BaseModel):
    total_questions: int
    total_time: str
    details: List[MessageDetail]

    class Config:
        schema_extra = {
            "example": {
                "total_questions": 3,
                "total_time": "2 days, 1:30:00",
                "details": [
                    {
                        "userId": "507f1f77bcf86cd799439011",
                        "question": "What is AI?",
                        "answer": "AI stands for Artificial Intelligence.",
                        "time": "2024-10-01T13:00:00"
                    },
                    {
                        "userId": "507f1f77bcf86cd799439012",
                        "question": "How does AI work?",
                        "answer": "AI works using algorithms and data.",
                        "time": "2024-10-02T14:00:00"
                    }
                ]
            }
        }
