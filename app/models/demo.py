from mongomock.object_id import ObjectId
from pydantic import BaseModel, EmailStr, ConfigDict


class BetaSignup(BaseModel):
    firstName: str
    email: EmailStr
    website: str
    goals: str
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "firstName": "John",
                "email": "<jon@gmail.com",
                "website": "https://gmail.com",
                "goals": "Bob",
            }

        }
    )