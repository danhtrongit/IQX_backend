"""Score Service - Business logic for score ranking and history."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.score.dtos import (
    ScoreRankingRequest,
    ScoreRankingResponse,
    ScoreRankingItem,
    ScoreHistoryRequest,
    ScoreHistoryResponse,
    ScoreHistoryItem,
)
from app.infrastructure.repositories.score_repo import ScoreRepository


class ScoreService:
    """Service for score ranking and history."""

    # Map common exchange names to database values
    EXCHANGE_MAP = {
        "HOSE": "HSX",
        "HO": "HSX",
    }

    def __init__(self, session: AsyncSession):
        self.repo = ScoreRepository(session)

    def _normalize_exchanges(self, exchange_str: str | None) -> list[str] | None:
        """Normalize exchange names to database values."""
        if not exchange_str:
            return None

        exchanges = []
        for e in exchange_str.split(","):
            e = e.strip().upper()
            # Map to database value if mapping exists
            exchanges.append(self.EXCHANGE_MAP.get(e, e))
        return exchanges

    async def get_ranking(self, request: ScoreRankingRequest) -> ScoreRankingResponse:
        """
        Get score ranking for all symbols.

        Args:
            request: ScoreRankingRequest with filters

        Returns:
            ScoreRankingResponse with ranked items
        """
        # Normalize exchange names
        exchanges = self._normalize_exchanges(request.exchange)

        # Get ranking from repository
        items, total = await self.repo.get_ranking(
            ma_period=request.ma_period.value,
            exchanges=exchanges,
            limit=request.limit,
            offset=request.offset,
            sort_desc=(request.sort.value == "desc"),
        )

        # Get trade date
        trade_date = await self.repo.get_latest_trade_date()

        # Convert to response DTOs
        ranking_items = [
            ScoreRankingItem(
                rank=item["rank"],
                symbol=item["symbol"],
                exchange=item["exchange"],
                score=item["score"],
                p=item["p"],
                v=item["v"],
                close=item["close"],
                ma=item["ma"],
                volume=item["volume"],
                vol_avg=item["vol_avg"],
            )
            for item in items
        ]

        return ScoreRankingResponse(
            items=ranking_items,
            total=total,
            ma_period=request.ma_period.value,
            trade_date=trade_date,
        )

    async def get_history(
        self,
        symbol: str,
        request: ScoreHistoryRequest,
    ) -> ScoreHistoryResponse:
        """
        Get score history for a single symbol.

        Args:
            symbol: Stock symbol
            request: ScoreHistoryRequest with filters

        Returns:
            ScoreHistoryResponse with history data
        """
        # Get history from repository
        items = await self.repo.get_history(
            symbol=symbol.upper(),
            ma_period=request.ma_period.value,
            time_range=request.range.value,
        )

        # Convert to response DTOs
        history_items = [
            ScoreHistoryItem(
                date=item["date"],
                score=item["score"],
                p=item["p"],
                v=item["v"],
                close=item["close"],
                ma=item["ma"],
                volume=item["volume"],
                vol_avg=item["vol_avg"],
            )
            for item in items
        ]

        return ScoreHistoryResponse(
            symbol=symbol.upper(),
            ma_period=request.ma_period.value,
            data=history_items,
        )
