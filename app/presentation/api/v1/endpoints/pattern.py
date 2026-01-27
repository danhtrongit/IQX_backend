"""Pattern API endpoints."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.application.pattern.services import pattern_service
from app.application.pattern.dtos import (
    CandlestickPatternListResponse,
    ChartPatternListResponse,
    StockPatternsResponse,
    PatternBySymbolResponse,
)

router = APIRouter(prefix="/patterns", tags=["patterns"])

ASSETS_DIR = Path(__file__).parent.parent.parent.parent.parent / "assets"


@router.get("/candlesticks", response_model=CandlestickPatternListResponse)
async def get_candlestick_patterns():
    """Get all candlestick pattern definitions."""
    return await pattern_service.get_all_candlestick_patterns()


@router.get("/charts", response_model=ChartPatternListResponse)
async def get_chart_patterns():
    """Get all chart pattern definitions."""
    return await pattern_service.get_all_chart_patterns()


@router.get("/stocks", response_model=StockPatternsResponse)
async def get_stock_patterns():
    """Get current stock patterns from Google Sheets."""
    try:
        return await pattern_service.get_all_stock_patterns()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{symbol}", response_model=PatternBySymbolResponse)
async def get_patterns_by_symbol(symbol: str):
    """Get patterns for a specific stock symbol."""
    try:
        return await pattern_service.get_patterns_by_symbol(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/candlesticks/{filename}")
async def get_candlestick_image(filename: str):
    """Get candlestick pattern image."""
    image_path = ASSETS_DIR / "candlesticks" / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/images/charts/{filename}")
async def get_chart_image(filename: str):
    """Get chart pattern image."""
    image_path = ASSETS_DIR / "patterns" / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/jpeg")
