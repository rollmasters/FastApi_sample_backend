from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.utils.object_id_pydantic_annotation import PyObjectId


class Person(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    date: Optional[datetime] = Field(
        alias="date",
        description="When the person was registered (Unix timestamp)",
        default=None
    )
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "date": "2024-10-04T10:20:30",
                "email": "jdoe@example.com",
            }
        },
    )


class SubscriptionCollection(BaseModel):
    people: list[Person]
