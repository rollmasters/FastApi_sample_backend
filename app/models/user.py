# app/models/user.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId
from typing import Optional
from datetime import datetime
from app.utils.object_id_pydantic_annotation import PyObjectId

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    name: str
    email: EmailStr
    password: Optional[bytes] = None  # Store as bytes since bcrypt works with bytes
    date: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False
    company_id: Optional[PyObjectId] = None  # Assuming it's a string
    is_company: bool = False
    promo: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, bytes: lambda x: x.decode()},
        json_schema_extra={
            "example": {
                "_id": "60d21b4667d0d8992e610c85",
                "name": "John Doe",
                "email": "jdoe@example.com",
                "password": "hashed_password",
                "date": "2024-10-05T12:34:56.789Z",
                "is_verified": False,
                "company_id": "company_id_if_any",
                "is_company": False,
                "promo": False,
            }
        },
    )
