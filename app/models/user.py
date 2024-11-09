from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId
from typing import Optional
from datetime import datetime
from app.utils.object_id_pydantic_annotation import PyObjectId

class UserInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id",  default_factory=PyObjectId)
    email: EmailStr
    hashed_password: Optional[str] = None
    is_active: bool = False
    is_verified: bool = False
    full_name: Optional[str] = None
    date_joined: datetime = Field(
        default_factory=datetime.utcnow,
        description="The date and time the user joined"
    )
    is_company: bool = False
    company_id: Optional[PyObjectId] = None
    promo: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId:str,ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "60d21b4667d0d8992e610c85",
                "email": "jdoe@example.com",
                "hashed_password": "hashedpassword123",
                "is_active": False,
                "is_verified": False,
                "full_name": "John Doe",
                "date_joined": "2024-10-05T12:34:56.789Z",
                "is_company": False,
                "company_id": None,
                "promo": False
            }
        },
    )
