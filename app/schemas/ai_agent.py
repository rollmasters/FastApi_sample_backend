from pydantic import BaseModel, Field
from typing import List, Optional

class AIResponse(BaseModel):
    question: str
    answer: str
    voice: Optional[str] = Field(alias='voice_answer')  # Corresponds to 'voice_answer' in JSON
    links: Optional[List[str]]
    process_time: Optional[float] = None  # Represented in seconds

    class Config:
        allow_population_by_field_name = True