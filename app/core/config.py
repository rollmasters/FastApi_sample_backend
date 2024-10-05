import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # Token expiry time in minutes

    # Email settings

    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@example.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM", "noreply@example.com")

    # MongoDB configuration

    MONGODB_DB_NAME: str = os.getenv("EMAIL_FROM_NAME", "MorseVerse")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")

    class Config:
        env_file = ".env"  # Load variables from .env file if it exists


# Create an instance of the Settings class
settings = Settings()
