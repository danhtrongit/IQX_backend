"""Services for pattern module."""
import json
import httpx
from pathlib import Path
from typing import Optional

from app.application.pattern.dtos import (
    CandlestickPatternDTO,
    ChartPatternDTO,
    StockCandlestickPatternDTO,
    StockChartPatternDTO,
    CandlestickPatternListResponse,
    ChartPatternListResponse,
    StockPatternsResponse,
    PatternBySymbolResponse,
)

# Google Sheets API URLs
PATTERN_SHEET_URL = "https://sheets.googleapis.com/v4/spreadsheets/1ekb2bYAQJZbtmqMUzsagb4uWBdtkAzTq3kuIMHQ22RI/values/pattern?key=AIzaSyB9PPBCGbWFv1TxH_8s_AsiqiChLs9MqXU"
MODEL_SHEET_URL = "https://sheets.googleapis.com/v4/spreadsheets/1ekb2bYAQJZbtmqMUzsagb4uWBdtkAzTq3kuIMHQ22RI/values/model?key=AIzaSyB9PPBCGbWFv1TxH_8s_AsiqiChLs9MqXU"

# Assets paths
ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"
CANDLESTICKS_JSON = ASSETS_DIR / "candlesticks" / "candlesticks.json"
PATTERNS_JSON = ASSETS_DIR / "patterns" / "patterns.json"


class PatternService:
    """Service for pattern analysis."""

    def __init__(self):
        self._candlesticks_data: Optional[dict] = None
        self._patterns_data: Optional[dict] = None
        self._candlestick_name_map: Optional[dict] = None
        self._pattern_name_map: Optional[dict] = None

    def _load_candlesticks_data(self) -> dict:
        """Load candlesticks data from JSON file."""
        if self._candlesticks_data is None:
            with open(CANDLESTICKS_JSON, "r", encoding="utf-8") as f:
                self._candlesticks_data = json.load(f)
            # Create name mapping for quick lookup
            self._candlestick_name_map = {
                p["name"]: p for p in self._candlesticks_data["candlesticks"]
            }
        return self._candlesticks_data

    def _load_patterns_data(self) -> dict:
        """Load chart patterns data from JSON file."""
        if self._patterns_data is None:
            with open(PATTERNS_JSON, "r", encoding="utf-8") as f:
                self._patterns_data = json.load(f)
            # Create name mapping for quick lookup (normalize names)
            self._pattern_name_map = {}
            for p in self._patterns_data["patterns"]:
                # Normalize: "Bull Channel" -> "BullChannel", "Rounding Bottom" -> "RoundingBottom"
                normalized = p["name"].replace(" ", "")
                self._pattern_name_map[normalized] = p
                # Also keep original
                self._pattern_name_map[p["name"]] = p
        return self._patterns_data

    async def get_all_candlestick_patterns(self) -> CandlestickPatternListResponse:
        """Get all candlestick patterns."""
        data = self._load_candlesticks_data()
        patterns = [
            CandlestickPatternDTO(**p) for p in data["candlesticks"]
        ]
        return CandlestickPatternListResponse(
            patterns=patterns,
            metadata=data["metadata"]
        )

    async def get_all_chart_patterns(self) -> ChartPatternListResponse:
        """Get all chart patterns."""
        data = self._load_patterns_data()
        patterns = [
            ChartPatternDTO(**p) for p in data["patterns"]
        ]
        return ChartPatternListResponse(
            patterns=patterns,
            metadata=data["metadata"]
        )

    async def fetch_stock_candlestick_patterns(self) -> list[StockCandlestickPatternDTO]:
        """Fetch stock candlestick patterns from Google Sheets."""
        async with httpx.AsyncClient() as client:
            response = await client.get(PATTERN_SHEET_URL, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        result = []
        rows = data.get("values", [])
        if len(rows) > 1:
            for row in rows[1:]:  # Skip header
                if len(row) >= 1:
                    symbol = row[0]
                    patterns = row[1:] if len(row) > 1 else []
                    result.append(StockCandlestickPatternDTO(
                        symbol=symbol,
                        patterns=patterns
                    ))
        return result

    async def fetch_stock_chart_patterns(self) -> list[StockChartPatternDTO]:
        """Fetch stock chart patterns from Google Sheets."""
        async with httpx.AsyncClient() as client:
            response = await client.get(MODEL_SHEET_URL, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        result = []
        rows = data.get("values", [])
        if len(rows) > 1:
            for row in rows[1:]:  # Skip header
                if len(row) >= 2:
                    result.append(StockChartPatternDTO(
                        symbol=row[0],
                        model=row[1]
                    ))
        return result

    async def get_all_stock_patterns(self) -> StockPatternsResponse:
        """Get all stock patterns from Google Sheets."""
        candlestick_patterns = await self.fetch_stock_candlestick_patterns()
        chart_patterns = await self.fetch_stock_chart_patterns()
        return StockPatternsResponse(
            candlestick_patterns=candlestick_patterns,
            chart_patterns=chart_patterns
        )

    async def get_patterns_by_symbol(self, symbol: str) -> PatternBySymbolResponse:
        """Get patterns for a specific symbol."""
        # Load reference data
        self._load_candlesticks_data()
        self._load_patterns_data()

        # Fetch stock patterns
        candlestick_stock_patterns = await self.fetch_stock_candlestick_patterns()
        chart_stock_patterns = await self.fetch_stock_chart_patterns()

        # Find candlestick patterns for symbol
        candlestick_patterns = []
        for stock in candlestick_stock_patterns:
            if stock.symbol.upper() == symbol.upper():
                for pattern_name in stock.patterns:
                    if pattern_name in self._candlestick_name_map:
                        candlestick_patterns.append(
                            CandlestickPatternDTO(**self._candlestick_name_map[pattern_name])
                        )
                break

        # Find chart pattern for symbol
        chart_pattern = None
        for stock in chart_stock_patterns:
            if stock.symbol.upper() == symbol.upper():
                model_name = stock.model
                if model_name in self._pattern_name_map:
                    chart_pattern = ChartPatternDTO(**self._pattern_name_map[model_name])
                break

        return PatternBySymbolResponse(
            symbol=symbol.upper(),
            candlestick_patterns=candlestick_patterns,
            chart_pattern=chart_pattern
        )


# Singleton instance
pattern_service = PatternService()
