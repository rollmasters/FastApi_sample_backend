from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta

from app.core.config import settings
from app.schemas.user import UserCreate, UserOut, Token
from app.models.user import UserInDB

from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.services.email import send_email
from app.database import get_db
from bson import ObjectId
from app.utils.object_id_pydantic_annotation import PyObjectId
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncIOMotorClient = Depends(get_db)):
    user_collection = db["Registered_users"]

    # Check if the email already exists
    existing_user = await user_collection.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate company_id if is_company is True
    company_id = PyObjectId() if user_in.is_company else None

    # Hash the password if provided
    hashed_password = get_password_hash(user_in.password) if user_in.password else None

    # Create the user
    user = UserInDB(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_company=user_in.is_company,
        company_id=str(company_id),
        promo=user_in.promo,
    )

    result = await user_collection.insert_one(user.model_dump(by_alias=True, exclude=["company_id"]))
    user.id = str(result.inserted_id)

    # Send verification email
    token_data = {"user_id": str(user.id)}
    verification_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
    verification_link = f"{settings.DOMAIN}/verify-email?token={verification_token}"
    email_body = f"""
    <html>
	    <head>
	        <title>Email Verification</title>
	    </head>
	    <body>
   <h2>Welcome to MORSE VERSE!</h2>
	        <p>Thank you for creating an account with us. 
	        We're excited to have you on board.
	         To start using your account, you just need to confirm your email address.</p>
	        <p>Click the link below to verify your email:</p>
    <p>
        <a href="{verification_link}">Verify Email</a>
    </p>
    <p>If you didn't create an account with MORSE VERSE, you can safely ignore this email.</p>
	        <p>Thanks,</p>
	        <p>Your friends at MORSE VERSE</p>
    </body>
    </html>
    """
    send_email(user.email, "Email Verification", email_body)

    return UserOut(**user.model_dump())


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorClient = Depends(get_db)
):
    user_collection = db["Registered_users"]
    user_data = await user_collection.find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    user = UserInDB(**user_data)
    if user.hashed_password:
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
    else:
        raise HTTPException(status_code=400, detail="Password not set for this user")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Email not verified")
    access_token = create_access_token(data={"user_id": str(user.id)})
    return Token(access_token=access_token)


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncIOMotorClient = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_collection = db["Users"]
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True, "is_verified": True}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="User not found or already verified")
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(email: str, db: AsyncIOMotorClient = Depends(get_db)):
    user_collection = db["Users"]
    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=400, detail="Email not found")
    user = UserInDB(**user_data)
    token_data = {"user_id": str(user.id)}
    reset_token = create_access_token(token_data, expires_delta=timedelta(hours=1))
    reset_link = f"http://yourdomain.com/reset-password?token={reset_token}"
    email_body = f"""
    <p>You requested a password reset.</p>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    """
    send_email(user.email, "Password Reset", email_body)
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(
        token: str, new_password: str, db: AsyncIOMotorClient = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_collection = db["Users"]
    hashed_password = get_password_hash(new_password)
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hashed_password}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="User not found")
    return {"message": "Password reset successful"}


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return UserOut(**current_user.dict())


@router.post("/logout")
async def logout():
    # Since JWT tokens are stateless, logout can be handled on the client side by deleting the token.
    return {"message": "Logout successful"}

# Optional: Implement social login endpoints if needed
# For example, Google Login
# This requires handling OAuth2 flows and is beyond the scope of this code snippet.
