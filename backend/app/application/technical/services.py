"""Technical Analysis Service."""

from typing import Protocol, Dict, Any, Optional

from app.application.technical.dtos import (
    TechnicalTimeframe,
    GaugeValues,
    GaugeData,
    IndicatorItem,
    PivotData,
    TechnicalAnalysisData,
    TechnicalAnalysisResponse,
)


class TechnicalDataProvider(Protocol):
    """Technical analysis data provider interface."""

    def get_technical_analysis(
        self,
        symbol: str,
        timeframe: str,
    ) -> Optional[Dict[str, Any]]:
        """Get technical analysis data."""
        ...


class TechnicalAnalysisService:
    """Service for technical analysis operations."""

    def __init__(self, data_provider: TechnicalDataProvider):
        self.data_provider = data_provider

    def get_technical_analysis(
        self,
        symbol: str,
        timeframe: str = TechnicalTimeframe.ONE_DAY.value,
    ) -> TechnicalAnalysisResponse:
        """
        Get technical analysis for a symbol.

        Args:
            symbol: Stock symbol (e.g., VIC, VNM)
            timeframe: ONE_HOUR, ONE_DAY, or ONE_WEEK

        Returns:
            TechnicalAnalysisResponse with data or error
        """
        symbol = symbol.upper()
        raw_data = self.data_provider.get_technical_analysis(symbol, timeframe)

        if raw_data is None:
            return TechnicalAnalysisResponse(
                symbol=symbol,
                timeframe=timeframe,
                data=None,
                error="Failed to fetch technical analysis data",
            )

        # Parse the raw data
        try:
            data = self._parse_technical_data(symbol, timeframe, raw_data)
            return TechnicalAnalysisResponse(
                symbol=symbol,
                timeframe=timeframe,
                data=data,
                error=None,
            )
        except Exception as e:
            return TechnicalAnalysisResponse(
                symbol=symbol,
                timeframe=timeframe,
                data=None,
                error=str(e),
            )

    def _parse_technical_data(
        self,
        symbol: str,
        timeframe: str,
        raw: Dict[str, Any],
    ) -> TechnicalAnalysisData:
        """Parse raw API response into TechnicalAnalysisData."""
        
        # Parse gauge data
        gauge_summary = self._parse_gauge(raw.get("gaugeSummary"))
        gauge_ma = self._parse_gauge(raw.get("gaugeMovingAverage"))
        gauge_osc = self._parse_gauge(raw.get("gaugeOscillator"))

        # Parse moving averages
        moving_averages = None
        raw_mas = raw.get("movingAverages")
        if raw_mas:
            moving_averages = [
                IndicatorItem(
                    name=ma.get("name", ""),
                    rating=ma.get("rating"),
                    value=self._safe_float(ma.get("value")),
                )
                for ma in raw_mas
            ]

        # Parse oscillators
        oscillators = None
        raw_oscs = raw.get("oscillators")
        if raw_oscs:
            oscillators = [
                IndicatorItem(
                    name=osc.get("name", ""),
                    rating=osc.get("rating"),
                    value=self._safe_float(osc.get("value")),
                )
                for osc in raw_oscs
            ]

        # Parse pivot data
        pivot = None
        raw_pivot = raw.get("pivot")
        if raw_pivot:
            pivot = PivotData(**{
                k: self._safe_float(v) for k, v in raw_pivot.items()
            })

        return TechnicalAnalysisData(
            symbol=symbol,
            timeframe=timeframe,
            price=self._safe_float(raw.get("price")),
            match_time=raw.get("matchTime"),
            gauge_summary=gauge_summary,
            gauge_moving_average=gauge_ma,
            gauge_oscillator=gauge_osc,
            moving_averages=moving_averages,
            oscillators=oscillators,
            pivot=pivot,
        )

    def _parse_gauge(self, raw: Optional[Dict[str, Any]]) -> Optional[GaugeData]:
        """Parse gauge data."""
        if not raw:
            return None
        
        values = None
        raw_values = raw.get("values")
        if raw_values:
            values = GaugeValues(
                buy=raw_values.get("BUY", 0),
                neutral=raw_values.get("NEUTRAL", 0),
                sell=raw_values.get("SELL", 0),
            )

        return GaugeData(
            rating=raw.get("rating"),
            values=values,
        )

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
