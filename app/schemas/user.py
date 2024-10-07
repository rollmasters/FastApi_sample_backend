from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[str] = Field(None, min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = None
    is_company: bool = False
    promo: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "password": "yourpassword",
                "full_name": "John Doe",
                "is_company": False,
                "promo": False
            }
        },
    )


class UserOut(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    is_active: bool
    is_verified: bool
    full_name: Optional[str] = None
    date_joined: datetime
    is_company: bool = False
    company_id: Optional[str] = None
    promo: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d21b4667d0d8992e610c85",
                "email": "jdoe@example.com",
                "is_active": True,
                "is_verified": True,
                "full_name": "John Doe",
                "date_joined": "2024-10-05T12:34:56.789Z",
                "is_company": False,
                "company_id": None,
                "promo": False
            }
        },
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "password": "yourpassword",
            }
        },
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "youraccesstoken",
                "token_type": "bearer",
            }
        },
    )
