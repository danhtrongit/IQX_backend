"""Vietcap IQ Technical Analysis Provider."""

import requests
from typing import Dict, Any, Optional
from enum import Enum


class TechnicalTimeframe(str, Enum):
    """Technical analysis timeframe options."""
    ONE_HOUR = "ONE_HOUR"
    ONE_DAY = "ONE_DAY"
    ONE_WEEK = "ONE_WEEK"


class VietcapTechnicalProvider:
    """Provider for Vietcap IQ Technical Analysis API."""

    BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1"
    HEADERS = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Origin": "https://iq.vietcap.com.vn",
        "Referer": "https://iq.vietcap.com.vn/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    def get_technical_analysis(
        self,
        symbol: str,
        timeframe: str = TechnicalTimeframe.ONE_DAY.value,
    ) -> Optional[Dict[str, Any]]:
        """
        Get technical analysis data for a symbol.

        Args:
            symbol: Stock symbol (e.g., VIC, VNM)
            timeframe: ONE_HOUR, ONE_DAY, or ONE_WEEK

        Returns:
            Technical analysis data or None if failed
        """
        url = f"{self.BASE_URL}/company/{symbol.upper()}/technical/{timeframe}"

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("successful") and data.get("code") == 0:
                return data.get("data")
            return None

        except requests.RequestException as e:
            print(f"Error fetching technical data for {symbol}: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing response for {symbol}: {e}")
            return None
