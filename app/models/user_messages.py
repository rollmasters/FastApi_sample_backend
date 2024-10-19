from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


from app.utils.object_id_pydantic_annotation import PyObjectId


class AIResponse(BaseModel):
    answer: str
    question: str
    links: Optional[List[str]]=None
    process_time: Optional[float]=None
    lang: Optional[str]=None
    voice: Optional[str] = Field(alias='voice_answer', default=None)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )


class UserMessages(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id',default_factory=PyObjectId)
    companyId: PyObjectId = Field(default_factory=PyObjectId, alias='companyId')
    userId: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='userId')
    AIResponses: AIResponse = Field(alias='messages')
    lang: Optional[str] = "EN-US"
    time: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
