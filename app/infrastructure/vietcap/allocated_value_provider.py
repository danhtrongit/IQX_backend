"""Vietcap Allocated Value Provider - Capital Flow by Sector."""

import requests
from typing import Dict, Any, Optional, List
from enum import Enum

from app.core.logging import get_logger

# Use vnstock's header generation for compatibility
try:
    from vnstock.core.utils.user_agent import get_headers
except ImportError:
    # Fallback if vnstock not available
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


class MarketGroup(str, Enum):
    """Market group options."""
    HOSE = "HOSE"
    HNX = "HNX"
    UPCOME = "UPCOME"
    ALL = "ALL"


class TimeFrame(str, Enum):
    """Time frame options."""
    ONE_DAY = "ONE_DAY"
    ONE_WEEK = "ONE_WEEK"
    ONE_MONTH = "ONE_MONTH"
    YTD = "YTD"
    ONE_YEAR = "ONE_YEAR"


class VietcapAllocatedValueProvider:
    """Provider for Vietcap Allocated Value API - Capital Flow by Sector."""

    BASE_URL = "https://trading.vietcap.com.vn/api/market-watch/AllocatedValue/getAllocatedValue"

    def __init__(self, random_agent: bool = True):
        """Initialize provider with vnstock-style headers."""
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)

    def get_allocated_value_sync(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get allocated value (capital flow by sector) - SYNC version.
        Uses same approach as vnstock library.

        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR

        Returns:
            List of sector allocations or None if failed
        """
        import json
        
        payload = json.dumps({
            "group": group.upper(),
            "timeFrame": time_frame.upper()
        })

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} - {response.reason}")
                return None
                
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Response might be a dict with nested lists
                return data
                
            logger.warning(f"Unexpected response format: {type(data)}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error fetching allocated value: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching allocated value: {e}")
            return None

    async def get_allocated_value(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Any]:
        """
        Get allocated value (capital flow by sector) - ASYNC wrapper.
        Runs sync request in thread pool for async compatibility.
        """
        from app.core.async_utils import run_sync
        return await run_sync(
            self.get_allocated_value_sync,
            group,
            time_frame
        )


class VietcapAllocatedICBProvider:
    """Provider for Vietcap Allocated ICB API - Sector allocation by Industry."""

    BASE_URL = "https://trading.vietcap.com.vn/api/market-watch/AllocatedICB/getAllocated"

    def __init__(self, random_agent: bool = True):
        """Initialize provider with vnstock-style headers."""
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)

    def get_allocated_icb_sync(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get allocated ICB (sector allocation by industry) - SYNC version.

        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR

        Returns:
            List of ICB sector allocations
        """
        import json
        
        payload = json.dumps({
            "group": group.upper(),
            "timeFrame": time_frame.upper()
        })

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} - {response.reason}")
                return None
                
            data = response.json()
            
            if isinstance(data, list):
                return data
                
            logger.warning(f"Unexpected response format: {type(data)}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error fetching allocated ICB: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching allocated ICB: {e}")
            return None

    async def get_allocated_icb(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get allocated ICB - ASYNC wrapper.
        """
        from app.core.async_utils import run_sync
        return await run_sync(
            self.get_allocated_icb_sync,
            group,
            time_frame
        )

    def get_allocated_icb_detail_sync(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
        icb_code: int = 9500,
    ) -> Optional[Dict[str, Any]]:
        """
        Get allocated ICB detail (stocks within a sector) - SYNC version.

        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR
            icb_code: ICB code to get details for

        Returns:
            Dict with sector info and icbDataDetail list of stocks
        """
        import json
        
        url = "https://trading.vietcap.com.vn/api/market-watch/AllocatedICB/getAllocatedDetail"
        payload = json.dumps({
            "group": group.upper(),
            "timeFrame": time_frame.upper(),
            "icbCode": icb_code
        })

        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} - {response.reason}")
                return None
                
            data = response.json()
            
            if isinstance(data, dict):
                return data
                
            logger.warning(f"Unexpected response format: {type(data)}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error fetching allocated ICB detail: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching allocated ICB detail: {e}")
            return None

    async def get_allocated_icb_detail(
        self,
        group: str = MarketGroup.HOSE.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
        icb_code: int = 9500,
    ) -> Optional[Dict[str, Any]]:
        """
        Get allocated ICB detail - ASYNC wrapper.
        """
        from app.core.async_utils import run_sync
        return await run_sync(
            self.get_allocated_icb_detail_sync,
            group,
            time_frame,
            icb_code
        )


class VietcapIndexImpactProvider:
    """Provider for Vietcap Index Impact API - Market leading stocks."""

    BASE_URL = "https://trading.vietcap.com.vn/api/market-watch/v2/IndexImpactChart/getData"

    def __init__(self, random_agent: bool = True):
        """Initialize provider with vnstock-style headers."""
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)

    def get_index_impact_sync(
        self,
        group: str = MarketGroup.ALL.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        """
        Get index impact (market leading stocks) - SYNC version.

        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR

        Returns:
            Dict with topUp and topDown lists of stocks
        """
        import json
        
        payload = json.dumps({
            "group": group.upper(),
            "timeFrame": time_frame.upper()
        })

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} - {response.reason}")
                return None
                
            data = response.json()
            
            if isinstance(data, dict):
                return data
                
            logger.warning(f"Unexpected response format: {type(data)}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error fetching index impact: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching index impact: {e}")
            return None

    async def get_index_impact(
        self,
        group: str = MarketGroup.ALL.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        """
        Get index impact - ASYNC wrapper.
        """
        from app.core.async_utils import run_sync
        return await run_sync(
            self.get_index_impact_sync,
            group,
            time_frame
        )


class VietcapTopProprietaryProvider:
    """Provider for Top Proprietary Trading API."""

    BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/market-watch/top-proprietary"

    def __init__(self, random_agent: bool = True):
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)

    def get_top_proprietary_sync(
        self,
        exchange: str = "ALL",
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        """Get top proprietary trading - SYNC version."""
        try:
            url = f"{self.BASE_URL}?timeFrame={time_frame.upper()}&exchange={exchange.upper()}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code}")
                return None
                
            data = response.json()
            if data.get("successful") and data.get("data"):
                return data["data"]
            return None

        except Exception as e:
            logger.error(f"Error fetching top proprietary: {e}")
            return None

    async def get_top_proprietary(
        self,
        exchange: str = "ALL",
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        from app.core.async_utils import run_sync
        return await run_sync(self.get_top_proprietary_sync, exchange, time_frame)


class VietcapForeignNetValueProvider:
    """Provider for Foreign Net Value API."""

    BASE_URL = "https://trading.vietcap.com.vn/api/market-watch/v3/ForeignNetValue/top"

    def __init__(self, random_agent: bool = True):
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)

    def get_foreign_net_value_sync(
        self,
        group: str = MarketGroup.ALL.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        """Get foreign net value (buy/sell) - SYNC version."""
        import json
        import time as time_module
        
        now = int(time_module.time())
        # Calculate from timestamp based on time frame
        timeframe_days = {
            "ONE_DAY": 1, "ONE_WEEK": 7, "ONE_MONTH": 30,
            "YTD": 365, "ONE_YEAR": 365
        }
        days = timeframe_days.get(time_frame.upper(), 7)
        from_ts = now - (days * 24 * 60 * 60)
        
        payload = json.dumps({
            "from": from_ts,
            "to": now,
            "group": group.upper(),
            "timeFrame": time_frame.upper()
        })

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code}")
                return None
                
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching foreign net value: {e}")
            return None

    async def get_foreign_net_value(
        self,
        group: str = MarketGroup.ALL.value,
        time_frame: str = TimeFrame.ONE_WEEK.value,
    ) -> Optional[Dict[str, Any]]:
        from app.core.async_utils import run_sync
        return await run_sync(self.get_foreign_net_value_sync, group, time_frame)

