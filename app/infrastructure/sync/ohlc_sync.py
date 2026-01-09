"""OHLC Sync Service - Fetch from VCI API and store in MySQL.

Usage:
    from app.infrastructure.sync.ohlc_sync import OHLCSyncService

    # Full sync (all symbols, 200 days)
    await OHLCSyncService.full_sync()

    # Daily sync (only today's data)
    await OHLCSyncService.daily_sync()

    # Check for gaps and auto-fill
    gaps = await OHLCSyncService.detect_gaps()
    await OHLCSyncService.fill_gaps()
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from vnstock.core.utils.user_agent import get_headers
from vnstock.api.listing import Listing

from app.infrastructure.db.session import async_session_factory
from app.infrastructure.models.ohlc_model import StockOHLCDailyModel

logger = logging.getLogger(__name__)


class OHLCSyncService:
    """Service to sync OHLC data from VCI API to MySQL."""

    API_URL = "https://api.vietcap.com.vn/ohlc-chart-service/v1/gap-chart"
    MAX_WORKERS = 50
    BATCH_INSERT_SIZE = 1000

    def __init__(self):
        self.headers = get_headers(data_source='VCI', random_agent=False)

    def _fetch_ohlc_single(self, symbol: str, count_back: int = 200) -> Optional[dict]:
        """Fetch OHLC data for a single symbol from VCI API."""
        params = {
            "symbol": symbol,
            "to": int(datetime.now().timestamp()),
            "timeFrame": "ONE_DAY",
            "countBack": count_back
        }
        try:
            resp = requests.get(
                self.API_URL,
                headers=self.headers,
                params=params,
                timeout=15
            )
            if resp.status_code == 200:
                result = resp.json()
                if result.get('success') and result.get('data'):
                    return {"symbol": symbol, **result['data']}
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")
        return None

    def fetch_bulk(self, symbols: list[str], count_back: int = 200) -> list[dict]:
        """Fetch OHLC data for multiple symbols in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {
                executor.submit(self._fetch_ohlc_single, s, count_back): s
                for s in symbols
            }

            for future in as_completed(futures):
                data = future.result()
                if data and data.get('o'):
                    results.append(data)

        return results

    @staticmethod
    def _parse_ohlc_records(data: dict) -> list[dict]:
        """Parse API response into list of OHLC records."""
        records = []
        symbol = data.get('symbol')

        timestamps = data.get('t', [])
        opens = data.get('o', [])
        highs = data.get('h', [])
        lows = data.get('l', [])
        closes = data.get('c', [])
        volumes = data.get('v', [])

        for i in range(len(timestamps)):
            try:
                ts = timestamps[i]
                # Handle string or int timestamp
                if isinstance(ts, str):
                    ts = int(ts)
                trade_date = datetime.fromtimestamp(ts).date()

                records.append({
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "open": Decimal(str(opens[i])),
                    "high": Decimal(str(highs[i])),
                    "low": Decimal(str(lows[i])),
                    "close": Decimal(str(closes[i])),
                    "volume": int(volumes[i]),
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse record {i} for {symbol}: {e}")
                continue

        return records

    async def _bulk_upsert(self, session: AsyncSession, records: list[dict]) -> int:
        """Bulk upsert OHLC records using MySQL ON DUPLICATE KEY UPDATE."""
        if not records:
            return 0

        inserted = 0
        # Process in batches - use executemany for better performance
        for i in range(0, len(records), self.BATCH_INSERT_SIZE):
            batch = records[i:i + self.BATCH_INSERT_SIZE]

            # Build multi-value INSERT statement for better performance
            values_list = []
            params = {}
            for idx, record in enumerate(batch):
                values_list.append(
                    f"(:symbol_{idx}, :trade_date_{idx}, :open_{idx}, :high_{idx}, "
                    f":low_{idx}, :close_{idx}, :volume_{idx}, NOW())"
                )
                params[f"symbol_{idx}"] = record["symbol"]
                params[f"trade_date_{idx}"] = record["trade_date"]
                params[f"open_{idx}"] = record["open"]
                params[f"high_{idx}"] = record["high"]
                params[f"low_{idx}"] = record["low"]
                params[f"close_{idx}"] = record["close"]
                params[f"volume_{idx}"] = record["volume"]

            query = text(f"""
                INSERT INTO stock_ohlc_daily
                    (symbol, trade_date, open, high, low, close, volume, created_at)
                VALUES {', '.join(values_list)}
                ON DUPLICATE KEY UPDATE
                    open = VALUES(open),
                    high = VALUES(high),
                    low = VALUES(low),
                    close = VALUES(close),
                    volume = VALUES(volume)
            """)

            await session.execute(query, params)
            await session.commit()
            inserted += len(batch)
            logger.info(f"Upserted batch: {inserted}/{len(records)}")

        return inserted

    async def full_sync(self, days: int = 200) -> dict:
        """
        Full sync: Fetch OHLC for all symbols and store in database.

        Args:
            days: Number of trading days to fetch (default: 200)

        Returns:
            dict with sync statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting full OHLC sync for {days} days...")

        # Get all symbols
        listing = Listing()
        all_stocks = listing.all_symbols(show=False)
        symbols = all_stocks['symbol'].tolist()
        logger.info(f"Found {len(symbols)} symbols to sync")

        # Fetch from API
        logger.info(f"Fetching OHLC data with {self.MAX_WORKERS} workers...")
        fetch_start = datetime.now()
        api_data = self.fetch_bulk(symbols, count_back=days)
        fetch_elapsed = (datetime.now() - fetch_start).total_seconds()
        logger.info(f"Fetched {len(api_data)} symbols in {fetch_elapsed:.2f}s")

        # Parse records
        all_records = []
        for data in api_data:
            records = self._parse_ohlc_records(data)
            all_records.extend(records)
        logger.info(f"Parsed {len(all_records)} OHLC records")

        # Bulk upsert to database
        async with async_session_factory() as session:
            inserted = await self._bulk_upsert(session, all_records)

        elapsed = (datetime.now() - start_time).total_seconds()

        stats = {
            "symbols_requested": len(symbols),
            "symbols_fetched": len(api_data),
            "records_upserted": inserted,
            "fetch_time_sec": fetch_elapsed,
            "total_time_sec": elapsed,
        }

        logger.info(f"Full sync completed: {stats}")
        return stats

    async def daily_sync(self) -> dict:
        """
        Daily sync: Fetch OHLC data and fill any gaps.
        Should be run after market close (after 15:30).

        Returns:
            dict with sync statistics
        """
        start_time = datetime.now()
        logger.info("Starting daily OHLC sync...")

        # First, check and fill any gaps (in case we missed some days)
        gaps_filled = 0
        async with async_session_factory() as session:
            result = await session.execute(text(
                "SELECT MAX(trade_date) FROM stock_ohlc_daily"
            ))
            last_date = result.scalar()

        today = date.today()
        if last_date and last_date < today - timedelta(days=1):
            # We have gaps, need to fill them
            days_missing = (today - last_date).days
            logger.info(f"Detected {days_missing} days gap, fetching missing data...")

            # Get all symbols
            listing = Listing()
            all_stocks = listing.all_symbols(show=False)
            symbols = all_stocks['symbol'].tolist()

            # Fetch enough days to cover the gap + today
            api_data = self.fetch_bulk(symbols, count_back=days_missing + 1)

            all_records = []
            for data in api_data:
                records = self._parse_ohlc_records(data)
                # Keep records from after last_date
                new_records = [r for r in records if r['trade_date'] > last_date]
                all_records.extend(new_records)

            async with async_session_factory() as session:
                gaps_filled = await self._bulk_upsert(session, all_records)

            # Calculate MA for all new dates
            for i in range(days_missing + 1):
                target_date = last_date + timedelta(days=i + 1)
                if target_date.weekday() < 5:  # Skip weekends
                    await self.calculate_ma(target_date=target_date)

            logger.info(f"Filled {gaps_filled} records for {days_missing} days")
        else:
            # No gaps, just sync today
            listing = Listing()
            all_stocks = listing.all_symbols(show=False)
            symbols = all_stocks['symbol'].tolist()

            # Fetch only 1 day (latest)
            api_data = self.fetch_bulk(symbols, count_back=1)

            all_records = []
            for data in api_data:
                records = self._parse_ohlc_records(data)
                today_records = [r for r in records if r['trade_date'] == today]
                all_records.extend(today_records)

            async with async_session_factory() as session:
                inserted = await self._bulk_upsert(session, all_records)

            # Calculate MA for today
            logger.info("Calculating MA for today's data...")
            await self.calculate_ma(target_date=today)

            gaps_filled = inserted

        elapsed = (datetime.now() - start_time).total_seconds()

        stats = {
            "date": str(today),
            "records_synced": gaps_filled,
            "total_time_sec": elapsed,
        }

        logger.info(f"Daily sync completed: {stats}")
        return stats

    async def sync_symbols(self, symbols: list[str], days: int = 200) -> dict:
        """
        Sync specific symbols.

        Args:
            symbols: List of symbols to sync
            days: Number of trading days to fetch

        Returns:
            dict with sync statistics
        """
        logger.info(f"Syncing {len(symbols)} symbols for {days} days...")

        api_data = self.fetch_bulk(symbols, count_back=days)

        all_records = []
        for data in api_data:
            records = self._parse_ohlc_records(data)
            all_records.extend(records)

        async with async_session_factory() as session:
            inserted = await self._bulk_upsert(session, all_records)

        return {
            "symbols_requested": len(symbols),
            "symbols_fetched": len(api_data),
            "records_upserted": inserted,
        }

    # =========================================================================
    # GAP DETECTION & AUTO-FILL
    # =========================================================================

    @staticmethod
    def _get_trading_days(start_date: date, end_date: date) -> set[date]:
        """Get expected trading days (weekdays only, excludes weekends)."""
        trading_days = set()
        current = start_date
        while current <= end_date:
            # Monday = 0, Friday = 4
            if current.weekday() < 5:
                trading_days.add(current)
            current += timedelta(days=1)
        return trading_days

    async def detect_gaps(self, days_back: int = 30) -> dict:
        """
        Detect missing trading days in the database.

        Args:
            days_back: Number of days to check (default: 30)

        Returns:
            dict with:
                - missing_dates: list of dates with no data
                - symbols_missing_data: dict of symbol -> list of missing dates
                - total_gaps: total number of gaps found
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        # Get expected trading days
        expected_days = self._get_trading_days(start_date, end_date)

        async with async_session_factory() as session:
            # Get dates that have data
            result = await session.execute(text("""
                SELECT DISTINCT trade_date
                FROM stock_ohlc_daily
                WHERE trade_date >= :start_date AND trade_date <= :end_date
                ORDER BY trade_date
            """), {"start_date": start_date, "end_date": end_date})
            existing_dates = {row[0] for row in result.fetchall()}

            # Get symbol count per date
            result = await session.execute(text("""
                SELECT trade_date, COUNT(DISTINCT symbol) as symbol_count
                FROM stock_ohlc_daily
                WHERE trade_date >= :start_date AND trade_date <= :end_date
                GROUP BY trade_date
                ORDER BY trade_date
            """), {"start_date": start_date, "end_date": end_date})
            date_coverage = {row[0]: row[1] for row in result.fetchall()}

            # Get total symbols
            result = await session.execute(text(
                "SELECT COUNT(DISTINCT symbol) FROM stock_ohlc_daily"
            ))
            total_symbols = result.scalar() or 0

        # Find completely missing dates
        missing_dates = sorted(expected_days - existing_dates)

        # Find dates with incomplete data (less than 80% of symbols)
        threshold = int(total_symbols * 0.8) if total_symbols > 0 else 100
        incomplete_dates = [
            d for d, count in date_coverage.items()
            if count < threshold
        ]

        gap_info = {
            "check_range": f"{start_date} to {end_date}",
            "expected_trading_days": len(expected_days),
            "dates_with_data": len(existing_dates),
            "missing_dates": [str(d) for d in missing_dates],
            "incomplete_dates": [
                {"date": str(d), "symbols": date_coverage.get(d, 0)}
                for d in incomplete_dates
            ],
            "total_symbols_in_db": total_symbols,
            "threshold_for_complete": threshold,
        }

        logger.info(f"Gap detection: {len(missing_dates)} missing dates, "
                    f"{len(incomplete_dates)} incomplete dates")

        return gap_info

    async def fill_gaps(self, days_back: int = 30) -> dict:
        """
        Detect and fill gaps in OHLC data.

        Args:
            days_back: Number of days to check and fill (default: 30)

        Returns:
            dict with fill statistics
        """
        logger.info(f"Starting gap fill for last {days_back} days...")

        # First detect gaps
        gaps = await self.detect_gaps(days_back)
        missing_dates = [
            datetime.strptime(d, "%Y-%m-%d").date()
            for d in gaps["missing_dates"]
        ]

        if not missing_dates:
            logger.info("No gaps found, all data is complete")
            return {"status": "no_gaps", "gaps": gaps}

        logger.info(f"Found {len(missing_dates)} missing dates, fetching data...")

        # Get all symbols
        listing = Listing()
        all_stocks = listing.all_symbols(show=False)
        symbols = all_stocks['symbol'].tolist()

        # For each missing date, we need to fetch data
        # Since API uses countBack, we fetch enough days to cover the gap
        oldest_missing = min(missing_dates)
        days_to_fetch = (date.today() - oldest_missing).days + 5

        # Fetch data
        api_data = self.fetch_bulk(symbols, count_back=days_to_fetch)

        # Parse and filter only missing dates
        missing_set = set(missing_dates)
        all_records = []
        for data in api_data:
            records = self._parse_ohlc_records(data)
            gap_records = [r for r in records if r['trade_date'] in missing_set]
            all_records.extend(gap_records)

        logger.info(f"Parsed {len(all_records)} records for missing dates")

        # Bulk upsert
        async with async_session_factory() as session:
            inserted = await self._bulk_upsert(session, all_records)

        return {
            "status": "filled",
            "missing_dates_found": len(missing_dates),
            "records_inserted": inserted,
            "dates_filled": [str(d) for d in missing_dates],
        }

    # =========================================================================
    # MOVING AVERAGE CALCULATION
    # =========================================================================

    MA_PERIODS = [5, 10, 20, 30, 50, 100, 200]

    async def calculate_ma(self, target_date: date | None = None) -> dict:
        """
        Calculate Moving Averages for all symbols.

        Uses window functions for efficient calculation.
        If target_date is None, calculates for all records with NULL MA values.

        Args:
            target_date: Specific date to calculate MA for (optional)

        Returns:
            dict with calculation statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting MA calculation for date: {target_date or 'all NULL records'}")

        async with async_session_factory() as session:
            # Get distinct symbols
            if target_date:
                result = await session.execute(text("""
                    SELECT DISTINCT symbol FROM stock_ohlc_daily
                    WHERE trade_date = :target_date
                """), {"target_date": target_date})
            else:
                result = await session.execute(text("""
                    SELECT DISTINCT symbol FROM stock_ohlc_daily
                    WHERE ma5 IS NULL
                """))
            symbols = [row[0] for row in result.fetchall()]

            logger.info(f"Processing {len(symbols)} symbols...")

            updated = 0
            for i, symbol in enumerate(symbols):
                await self._calculate_ma_for_symbol(session, symbol, target_date)
                updated += 1
                if (i + 1) % 100 == 0:
                    logger.info(f"Progress: {i + 1}/{len(symbols)} symbols")
                    await session.commit()

            await session.commit()

        elapsed = (datetime.now() - start_time).total_seconds()

        stats = {
            "symbols_processed": updated,
            "target_date": str(target_date) if target_date else "all_null",
            "elapsed_seconds": elapsed,
        }

        logger.info(f"MA calculation completed: {stats}")
        return stats

    async def _calculate_ma_for_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        target_date: date | None = None
    ) -> None:
        """Calculate MA for a single symbol by fetching data and updating."""
        # Get all records for this symbol
        if target_date:
            records_query = text("""
                SELECT id, trade_date, close, volume
                FROM stock_ohlc_daily
                WHERE symbol = :symbol AND trade_date = :target_date
                ORDER BY trade_date ASC
            """)
            params = {"symbol": symbol, "target_date": target_date}
        else:
            records_query = text("""
                SELECT id, trade_date, close, volume
                FROM stock_ohlc_daily
                WHERE symbol = :symbol AND ma5 IS NULL
                ORDER BY trade_date ASC
            """)
            params = {"symbol": symbol}

        result = await session.execute(records_query, params)
        target_records = result.fetchall()

        if not target_records:
            return

        # Get all historical data for this symbol (needed for MA calculation)
        history_query = text("""
            SELECT trade_date, close, volume
            FROM stock_ohlc_daily
            WHERE symbol = :symbol
            ORDER BY trade_date ASC
        """)
        history_result = await session.execute(history_query, {"symbol": symbol})
        all_data = history_result.fetchall()

        # Build lookup for quick access
        date_to_idx = {row[0]: i for i, row in enumerate(all_data)}
        closes = [float(row[1]) for row in all_data]
        volumes = [int(row[2]) for row in all_data]

        # Calculate MA for each target record
        for record in target_records:
            record_id = record[0]
            record_date = record[1]
            idx = date_to_idx.get(record_date)

            if idx is None:
                continue

            ma_values = {}
            for period in self.MA_PERIODS:
                start_idx = max(0, idx - period + 1)
                if idx - start_idx + 1 >= period:
                    # Have enough data
                    ma_closes = closes[start_idx:idx + 1]
                    ma_volumes = volumes[start_idx:idx + 1]
                    ma_values[f"ma{period}"] = sum(ma_closes) / len(ma_closes)
                    ma_values[f"vol_ma{period}"] = int(sum(ma_volumes) / len(ma_volumes))
                else:
                    ma_values[f"ma{period}"] = None
                    ma_values[f"vol_ma{period}"] = None

            # Update record
            update_query = text("""
                UPDATE stock_ohlc_daily
                SET ma5 = :ma5, ma10 = :ma10, ma20 = :ma20, ma30 = :ma30,
                    ma50 = :ma50, ma100 = :ma100, ma200 = :ma200,
                    vol_ma5 = :vol_ma5, vol_ma10 = :vol_ma10, vol_ma20 = :vol_ma20,
                    vol_ma30 = :vol_ma30, vol_ma50 = :vol_ma50, vol_ma100 = :vol_ma100,
                    vol_ma200 = :vol_ma200
                WHERE id = :id
            """)
            await session.execute(update_query, {"id": record_id, **ma_values})

    async def calculate_ma_batch(self, batch_size: int = 50) -> dict:
        """
        Calculate MA in batches for better performance.

        This is an optimized version that processes symbols in batches
        and uses a single transaction per batch.

        Args:
            batch_size: Number of symbols per batch

        Returns:
            dict with calculation statistics
        """
        start_time = datetime.now()
        logger.info("Starting batch MA calculation...")

        async with async_session_factory() as session:
            # Get all symbols that need MA calculation
            result = await session.execute(text("""
                SELECT DISTINCT symbol FROM stock_ohlc_daily
                WHERE ma5 IS NULL
            """))
            symbols = [row[0] for row in result.fetchall()]

            if not symbols:
                logger.info("No symbols need MA calculation")
                return {"status": "no_work", "symbols": 0}

            logger.info(f"Found {len(symbols)} symbols needing MA calculation")

            total_updated = 0
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]

                for symbol in batch:
                    await self._calculate_ma_for_symbol(session, symbol)

                await session.commit()
                total_updated += len(batch)
                logger.info(f"Batch progress: {total_updated}/{len(symbols)} symbols")

        elapsed = (datetime.now() - start_time).total_seconds()

        return {
            "symbols_processed": total_updated,
            "elapsed_seconds": elapsed,
            "status": "completed",
        }

    async def get_sync_status(self) -> dict:
        """
        Get current sync status and health check.

        Returns:
            dict with sync status information
        """
        async with async_session_factory() as session:
            # Total records
            result = await session.execute(text(
                "SELECT COUNT(*) FROM stock_ohlc_daily"
            ))
            total_records = result.scalar()

            # Total symbols
            result = await session.execute(text(
                "SELECT COUNT(DISTINCT symbol) FROM stock_ohlc_daily"
            ))
            total_symbols = result.scalar()

            # Date range
            result = await session.execute(text("""
                SELECT MIN(trade_date), MAX(trade_date)
                FROM stock_ohlc_daily
            """))
            row = result.fetchone()
            min_date, max_date = row if row else (None, None)

            # Latest sync (most recent trade_date)
            result = await session.execute(text("""
                SELECT trade_date, COUNT(*) as count
                FROM stock_ohlc_daily
                WHERE trade_date = (SELECT MAX(trade_date) FROM stock_ohlc_daily)
                GROUP BY trade_date
            """))
            latest = result.fetchone()
            latest_date = latest[0] if latest else None
            latest_count = latest[1] if latest else 0

        return {
            "total_records": total_records,
            "total_symbols": total_symbols,
            "date_range": {
                "from": str(min_date) if min_date else None,
                "to": str(max_date) if max_date else None,
            },
            "latest_sync": {
                "date": str(latest_date) if latest_date else None,
                "symbols_count": latest_count,
            },
            "health": "healthy" if latest_count > 1000 else "needs_sync",
        }


# Singleton instance
ohlc_sync_service = OHLCSyncService()
