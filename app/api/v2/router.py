from fastapi import APIRouter

from .endpoints import subscription, auth

api_router = APIRouter()

api_router.include_router(subscription.router, tags=["subscriptions"])
api_router.include_router(auth.router, tags=["authentication"])
