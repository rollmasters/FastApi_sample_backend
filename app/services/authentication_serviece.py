from jose import jwt, JWTError

from app.core.config import settings


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return {"user_id": user_id}
    except JWTError:
        return None
