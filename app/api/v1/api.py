"""API v1 router aggregator"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    signals,
    towers,
    calculations,
    reports,
    speed_tests,
    analysis,
    recommendations
)
from app.api.v1.endpoints import integration_opencellid

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signal Measurements"])
api_router.include_router(towers.router, prefix="/towers", tags=["Towers"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["RF Calculations"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(speed_tests.router, prefix="/speed-tests", tags=["Speed Tests"])
api_router.include_router(analysis.router, tags=["Analysis"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(integration_opencellid.router, prefix="/integration/opencellid", tags=["Integration"]) 

