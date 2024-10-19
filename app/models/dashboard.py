from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

from app.utils.object_id_pydantic_annotation import PyObjectId


class Settings(BaseModel):
    companyId: PyObjectId = Field(..., alias='companyId')
    chatEnabled: bool = Field(..., alias='chatEnabled')
    creative: bool = Field(..., alias='creative')
    unknown: bool = Field(..., alias='unknown')
    url: Optional[str] = Field(None, alias='url')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

class TableData(BaseModel):
    companyId: str = Field(..., alias='companyId')
    title: str
    date: datetime
    status: str
    statusClass: str
    progress: int

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

class FileUploadResponse(BaseModel):
    fileName: str
    fileUrl: str

class AIInfo(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    companyId: str = Field(..., alias='companyId')
    enterpriseName: Optional[str] = Field('', alias='enterpriseName')
    website: Optional[str] = ''
    industry: Optional[str] = ''
    description: Optional[str] = ''
    agentName: Optional[str] = Field('', alias='agentName')
    commonInquiries: Optional[List[str]] = Field(default_factory=list, alias='commonInquiries')
    adjustments: Optional[str] = ''
    language: Optional[str] = Field('English', alias='language')
    documentationLinks: Optional[List[FileUploadResponse]] = Field(default_factory=list, alias='documentationLinks')
    referredLinks: Optional[List[str]] = Field(default_factory=list, alias='referredLinks')

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )


class Preferences(BaseModel):
    company_id: str = Field(..., alias="company_id")
    office: str = Field(default="option1")
    character: str = Field(default="option1")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )

class BugReport(BaseModel):
    company_id: str = Field(..., alias="company_id")
    report_description: str
    steps: str
    contact: Optional[bool] = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )


class SummaryResponse(BaseModel):
    total_questions: int
    total_time: str
    details: List[dict]

    class Config:
        schema_extra = {
            "example": {
                "total_questions": 5,
                "total_time": "30m20s",
                "details": [
                    {
                        "userId": "507f1f77bcf86cd799439011",
                        "question": "What is AI?",
                        "answer": "AI stands for Artificial Intelligence.",
                        "time": "2024-10-01T13:00:00"
                    }
                ]
            }
        }