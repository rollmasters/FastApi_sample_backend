from fastapi import APIRouter

from .endpoints import subscription, auth, betasignup, google_cloud, ai_agent,dashboard

api_router = APIRouter()

api_router.include_router(subscription.router, tags=["subscriptions"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(betasignup.router, tags=["damo"])

api_router.include_router(google_cloud.router, tags=["Google cloud"])

api_router.include_router(ai_agent.router, tags=["AI_agent"])

api_router.include_router(dashboard.router, tags=["Dashboard"])