"""API v1 main router."""
from fastapi import APIRouter

from app.presentation.api.v1.endpoints import (
    auth,
    symbols,
    quotes,
    financials,
    company,
    trading,
    ws,
    market,
    insight,
    chat,
    cache,
    listing,
    technical,
)

api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(symbols.router)
api_router.include_router(quotes.router)
api_router.include_router(financials.router)
api_router.include_router(company.router)
api_router.include_router(trading.router)
api_router.include_router(ws.router)
api_router.include_router(market.router)
api_router.include_router(insight.router)
api_router.include_router(chat.router)
api_router.include_router(cache.router)
api_router.include_router(listing.router)
api_router.include_router(technical.router)

