"""Score API endpoints for ranking and history."""
from fastapi import APIRouter, Query, Path

from app.application.score.dtos import (
    MAPeriod,
    MAPeriodHistory,
    TimeRange,
    SortOrder,
    ScoreRankingResponse,
    ScoreHistoryResponse,
    ScoreRankingRequest,
    ScoreHistoryRequest,
)
from app.application.score.services import ScoreService
from app.presentation.deps.auth_deps import DBSession


router = APIRouter(prefix="/score", tags=["Score"])


@router.get("/ranking", response_model=ScoreRankingResponse)
async def get_score_ranking(
    db: DBSession,
    ma_period: MAPeriod = Query(..., description="Moving Average period"),
    exchange: str | None = Query(
        None,
        description="Comma-separated exchange codes (e.g., 'HOSE,HNX')",
    ),
    limit: int = Query(50, ge=1, le=500, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort: SortOrder = Query(SortOrder.DESC, description="Sort order"),
) -> ScoreRankingResponse:
    """
    Get score ranking for all symbols.

    **Score Formula:** SCORE = P × √V
    - P = ((Close - MA) / MA) × 100 (price deviation percentage)
    - V = Volume / Vol_Avg (volume ratio)

    **Filter by:**
    - MA period: 5, 10, 20, 30, 50, 100, 200
    - Exchange: HOSE, HNX, UPCOM (comma-separated)

    **Returns:** Ranked list of symbols with score details.
    """
    request = ScoreRankingRequest(
        ma_period=ma_period,
        exchange=exchange,
        limit=limit,
        offset=offset,
        sort=sort,
    )

    service = ScoreService(db)
    return await service.get_ranking(request)


@router.get("/history/{symbol}", response_model=ScoreHistoryResponse)
async def get_score_history(
    db: DBSession,
    symbol: str = Path(..., description="Stock symbol"),
    ma_period: MAPeriodHistory = Query(..., description="Moving Average period"),
    range: TimeRange = Query(..., alias="range", description="Time range"),
) -> ScoreHistoryResponse:
    """
    Get score history for a single symbol.

    **Score Formula:** SCORE = P × √V
    - P = ((Close - MA) / MA) × 100 (price deviation percentage)
    - V = Volume / Vol_Avg (volume ratio)

    **Filter by:**
    - MA period: 5, 10, 20, 30, 50, 100 (no 200)
    - Time range: week (7 days), month (30 days), year (365 days)

    **Returns:** Historical score data for charting.
    """
    request = ScoreHistoryRequest(
        ma_period=ma_period,
        range=range,
    )

    service = ScoreService(db)
    return await service.get_history(symbol, request)
