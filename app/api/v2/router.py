from fastapi import APIRouter

from .endpoints import subscription
api_router = APIRouter()

api_router.include_router(subscription.router, tags=["subscriptions"])