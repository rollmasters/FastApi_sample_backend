from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.database import get_db
from app.models.user import UserInDB
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    :param password: The plain-text password to hash.
    :return: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain-text password matches the hashed password.

    :param plain_password: The plain-text password.
    :param hashed_password: The hashed password.
    :return: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates a JWT access token.

    :param data: The data to include in the token payload.
    :param expires_delta: The time delta after which the token expires.
    :return: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes a JWT access token.

    :param token: The JWT token to decode.
    :return: The decoded token payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncIOMotorClient = Depends(get_db)
) -> UserInDB:
    """
    Retrieves the current authenticated user based on the JWT token.

    :param token: The JWT token extracted from the request.
    :param db: The database client instance.
    :return: The UserInDB instance representing the current user.
    :raises HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    user_id = payload.get("user_id")
    if not user_id:
        raise credentials_exception
    user_data = await db["Users"].find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise credentials_exception
    return UserInDB(**user_data)


def validate_object_id(id_str: str):
    """Validate that the provided string is a valid MongoDB ObjectId."""
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {id_str}")
    return ObjectId(id_str)  # Return the valid ObjectId instance