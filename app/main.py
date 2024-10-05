from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v2.router import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db

# Initialize FastAPI app

origins = [
    "http://localhost:3000",
    "https://www.morseverse.com",
    "https://morseverse.com/ai_agent"
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    await init_db()
    yield
    # Shutdown: Close DB
    await close_db()


app = FastAPI(
    title="morseverse",
    description="website apis ",
    version="2.0.0",
    lifespan=lifespan

)
# Middleware (e.g., for CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Update this with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routers
app.include_router(api_router, prefix="/api/v2")

# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
