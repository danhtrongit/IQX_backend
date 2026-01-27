"""Vietcap Sector Provider - Sector Information & Ranking APIs.

Provides access to:
- Sector Information (market cap, performance metrics)
- Sector Ranking (daily rankings with trends)
- ICB Codes (sector code mappings)
- Trading Dates
- Sector Companies (stocks within a sector)
- Sector Index History (price trend data)
"""

import requests
from typing import Dict, Any, Optional, List
from enum import Enum

from app.core.logging import get_logger

# Use vnstock's header generation for compatibility
try:
    from vnstock.core.utils.user_agent import get_headers
except ImportError:
    def get_headers(data_source='VCI', random_agent=True, **kwargs):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Origin': 'https://trading.vietcap.com.vn',
            'Referer': 'https://trading.vietcap.com.vn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        }

logger = get_logger(__name__)


class ICBLevel(int, Enum):
    """ICB Level options."""
    LEVEL_1 = 1  # Industry (e.g., Financials)
    LEVEL_2 = 2  # Supersector (e.g., Banks)
    LEVEL_3 = 3  # Sector (e.g., Commercial Banks)
    LEVEL_4 = 4  # Subsector (e.g., State-owned Banks)


class VietcapSectorProvider:
    """Provider for Vietcap Sector APIs - IQ Sector Intelligence."""

    BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1"

    def __init__(self, random_agent: bool = True):
        """Initialize provider with vnstock-style headers."""
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)
        # Additional headers for iq.vietcap.com.vn
        self.headers.update({
            'Origin': 'https://trading.vietcap.com.vn',
            'Referer': 'https://trading.vietcap.com.vn/',
        })

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Make GET request to API endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error {response.status_code} for {endpoint}")
                return None
                
            data = response.json()
            
            # Handle wrapped responses
            if isinstance(data, dict) and 'data' in data:
                return data.get('data')
            return data

        except requests.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

    # === SYNC Methods ===

    def get_sector_information_sync(
        self,
        icb_level: int = ICBLevel.LEVEL_2.value
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get sector information with performance metrics.

        Returns list of sectors with:
        - icbCode: Sector code
        - marketCap: Market capitalization
        - last20DayIndex: Sparkline data for 20 days
        - lastCloseIndex: Last closing index value
        - percentPriceChange1Day, 1Week, 1Month, 6Month, YTD, 1Year, 2Year, 5Year
        """
        return self._make_request(
            "sector-information",
            params={"icbLevel": icb_level}
        )

    def get_sector_ranking_sync(
        self,
        icb_level: int = ICBLevel.LEVEL_2.value,
        adtv: int = 3,
        value: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get sector ranking with daily trends.

        Returns list of sectors with:
        - name: ICB code
        - values: Array of { date, value, sectorTrend }
        """
        return self._make_request(
            "sector-ranking/sectors",
            params={"icbLevel": icb_level, "adtv": adtv, "value": value}
        )

    def get_icb_codes_sync(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get ICB codes mapping.

        Returns list with:
        - name: ICB code
        - enSector: English sector name
        - viSector: Vietnamese sector name
        - icbLevel: Level (1-4)
        - isLevel1Custom: Boolean
        """
        return self._make_request("sectors/icb-codes")

    def get_trading_dates_sync(self) -> Optional[List[str]]:
        """
        Get recent trading dates.

        Returns list of date strings (YYYY-MM-DD format).
        """
        return self._make_request("sector-ranking/trading-date")

    def get_sector_companies_sync(
        self,
        icb_code: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get companies within a sector.

        Returns list of stocks with:
        - ticker: Stock symbol
        - organShortNameVi: Company name (Vietnamese)
        - marketCap: Market capitalization
        - latestPrice: Current price
        - percentPriceChange: 1-day change %
        - ttmPe, ttmPb, ttmEps: Valuation metrics
        - roe, roa: Profitability metrics
        - averageMatchVolume1Month: Avg volume
        - foreignRoom: Foreign ownership room
        """
        return self._make_request(f"sector-information/{icb_code}/companies")

    def get_sector_index_history_sync(
        self,
        icb_codes: List[int],
        icb_level: int = ICBLevel.LEVEL_2.value,
        number_of_days: str = "ALL"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get sector index history for charting.

        Args:
            icb_codes: List of ICB codes to fetch
            icb_level: ICB level (1-4)
            number_of_days: Number of days or "ALL"

        Returns list with:
        - icbCode: Sector code
        - data: Array of { date, value }
        """
        icb_codes_str = ",".join(str(c) for c in icb_codes)
        return self._make_request(
            "sectors/icb-index",
            params={
                "icbLevel": icb_level,
                "icbCodes": icb_codes_str,
                "enNumberOfDays": number_of_days
            }
        )

    # === ASYNC Wrappers ===

    async def get_sector_information(
        self,
        icb_level: int = ICBLevel.LEVEL_2.value
    ) -> Optional[List[Dict[str, Any]]]:
        """Get sector information - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(self.get_sector_information_sync, icb_level)

    async def get_sector_ranking(
        self,
        icb_level: int = ICBLevel.LEVEL_2.value,
        adtv: int = 3,
        value: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """Get sector ranking - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(self.get_sector_ranking_sync, icb_level, adtv, value)

    async def get_icb_codes(self) -> Optional[List[Dict[str, Any]]]:
        """Get ICB codes - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(self.get_icb_codes_sync)

    async def get_trading_dates(self) -> Optional[List[str]]:
        """Get trading dates - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(self.get_trading_dates_sync)

    async def get_sector_companies(
        self,
        icb_code: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Get sector companies - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(self.get_sector_companies_sync, icb_code)

    async def get_sector_index_history(
        self,
        icb_codes: List[int],
        icb_level: int = ICBLevel.LEVEL_2.value,
        number_of_days: str = "ALL"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get sector index history - ASYNC wrapper."""
        from app.core.async_utils import run_sync
        return await run_sync(
            self.get_sector_index_history_sync,
            icb_codes,
            icb_level,
            number_of_days
        )
