"""Score Repository - Query logic for score ranking and history."""
import math
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ScoreRepository:
    """Repository for querying score data from OHLC table."""

    MA_COLUMNS = {
        5: ("ma5", "vol_ma5"),
        10: ("ma10", "vol_ma10"),
        20: ("ma20", "vol_ma20"),
        30: ("ma30", "vol_ma30"),
        50: ("ma50", "vol_ma50"),
        100: ("ma100", "vol_ma100"),
        200: ("ma200", "vol_ma200"),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_trade_date(self) -> date | None:
        """Get the most recent trade date in the database."""
        result = await self.session.execute(text(
            "SELECT MAX(trade_date) FROM stock_ohlc_daily"
        ))
        return result.scalar()

    async def get_ranking(
        self,
        ma_period: int,
        exchanges: list[str] | None,
        limit: int,
        offset: int,
        sort_desc: bool,
        trade_date: date | None = None,
    ) -> tuple[list[dict], int]:
        """
        Get score ranking for all symbols.

        Args:
            ma_period: MA period (5, 10, 20, 30, 50, 100, 200)
            exchanges: List of exchange codes to filter (None = all)
            limit: Max items to return
            offset: Offset for pagination
            sort_desc: True for highest score first
            trade_date: Specific date (default: latest)

        Returns:
            Tuple of (list of score items, total count)
        """
        if trade_date is None:
            trade_date = await self.get_latest_trade_date()
            if trade_date is None:
                return [], 0

        ma_col, vol_ma_col = self.MA_COLUMNS.get(ma_period, ("ma20", "vol_ma20"))

        # Build WHERE clause
        where_conditions = [
            "o.trade_date = :trade_date",
            f"o.{ma_col} IS NOT NULL",
            f"o.{vol_ma_col} IS NOT NULL",
            f"o.{vol_ma_col} > 0",
            "o.volume >= 500000",  # Filter out low volume stocks
        ]
        params = {"trade_date": trade_date, "limit": limit, "offset": offset}

        if exchanges:
            where_conditions.append("s.exchange IN :exchanges")
            params["exchanges"] = tuple(exchanges)

        where_clause = " AND ".join(where_conditions)
        sort_order = "DESC" if sort_desc else "ASC"

        # Main query with score calculation
        query = text(f"""
            SELECT
                o.symbol,
                s.exchange,
                o.close,
                o.{ma_col} as ma,
                o.volume,
                o.{vol_ma_col} as vol_avg,
                ((o.close - o.{ma_col}) / o.{ma_col}) * 100 as p,
                o.volume / o.{vol_ma_col} as v
            FROM stock_ohlc_daily o
            JOIN symbols s ON o.symbol = s.symbol
            WHERE {where_clause}
            ORDER BY p * SQRT(o.volume / o.{vol_ma_col}) {sort_order}
            LIMIT :limit OFFSET :offset
        """)

        result = await self.session.execute(query, params)
        rows = result.fetchall()

        # Calculate score and build response
        items = []
        for i, row in enumerate(rows):
            p = float(row[6]) if row[6] else 0.0
            v = float(row[7]) if row[7] else 0.0
            score = p * math.sqrt(v) if v > 0 else 0.0

            items.append({
                "rank": offset + i + 1,
                "symbol": row[0],
                "exchange": row[1],
                "score": round(score, 4),
                "p": round(p, 4),
                "v": round(v, 4),
                "close": row[2],
                "ma": row[3],
                "volume": row[4],
                "vol_avg": row[5],
            })

        # Count total
        count_query = text(f"""
            SELECT COUNT(*)
            FROM stock_ohlc_daily o
            JOIN symbols s ON o.symbol = s.symbol
            WHERE {where_clause}
        """)
        count_result = await self.session.execute(count_query, params)
        total = count_result.scalar() or 0

        return items, total

    async def get_history(
        self,
        symbol: str,
        ma_period: int,
        time_range: str,
    ) -> list[dict]:
        """
        Get score history for a single symbol.

        Args:
            symbol: Stock symbol
            ma_period: MA period (5, 10, 20, 30, 50, 100)
            time_range: "week", "month", or "year"

        Returns:
            List of score history items
        """
        # Calculate date range
        end_date = date.today()
        if time_range == "week":
            start_date = end_date - timedelta(days=7)
        elif time_range == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)

        ma_col, vol_ma_col = self.MA_COLUMNS.get(ma_period, ("ma20", "vol_ma20"))

        query = text(f"""
            SELECT
                trade_date,
                close,
                {ma_col} as ma,
                volume,
                {vol_ma_col} as vol_avg
            FROM stock_ohlc_daily
            WHERE symbol = :symbol
              AND trade_date >= :start_date
              AND trade_date <= :end_date
              AND {ma_col} IS NOT NULL
              AND {vol_ma_col} IS NOT NULL
              AND {vol_ma_col} > 0
            ORDER BY trade_date ASC
        """)

        result = await self.session.execute(query, {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
        })
        rows = result.fetchall()

        items = []
        for row in rows:
            close = float(row[1])
            ma = float(row[2])
            volume = int(row[3])
            vol_avg = int(row[4])

            p = ((close - ma) / ma) * 100 if ma > 0 else 0.0
            v = volume / vol_avg if vol_avg > 0 else 0.0
            score = p * math.sqrt(v) if v > 0 else 0.0

            items.append({
                "date": row[0],
                "score": round(score, 4),
                "p": round(p, 4),
                "v": round(v, 4),
                "close": Decimal(str(close)),
                "ma": Decimal(str(ma)),
                "volume": volume,
                "vol_avg": vol_avg,
            })

        return items
