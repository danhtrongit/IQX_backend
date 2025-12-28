"""Macro application services for Vietnamese macroeconomic data."""
from typing import List, Dict, Any

from app.core.logging import get_logger
from app.core.async_utils import run_sync
from app.application.macro.dtos import (
    MacroDataItem,
    MacroResponse,
    GDPResponse,
    CPIResponse,
    ExchangeRateResponse,
    ImportExportResponse,
    FDIResponse,
    MoneySupplyResponse,
)
from app.infrastructure.vnstock.macro_provider import VnstockMacroProvider

logger = get_logger(__name__)


class MacroService:
    """Service for Vietnamese macroeconomic data."""

    def __init__(self, source: str = "mbk"):
        self.provider = VnstockMacroProvider(source=source)

    def _convert_to_items(self, data: List[Dict[str, Any]]) -> List[MacroDataItem]:
        """Convert raw data to MacroDataItem list."""
        items = []
        for row in data:
            item = MacroDataItem(
                report_time=row.get("report_time") or row.get("reportTime"),
                group_name=row.get("group_name") or row.get("groupName"),
                name=row.get("name"),
                value=self._safe_float(row.get("value")),
                unit=row.get("unit"),
                source=row.get("source"),
                report_type=row.get("report_type") or row.get("reportType"),
            )
            items.append(item)
        return items

    @staticmethod
    def _safe_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    async def get_gdp(self, limit: int = 20) -> GDPResponse:
        """Get GDP data."""
        def _fetch():
            return self.provider.get_gdp(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return GDPResponse(
            data_type="gdp",
            data=items,
            count=len(items),
        )

    async def get_cpi(self, limit: int = 20) -> CPIResponse:
        """Get CPI (Consumer Price Index) data."""
        def _fetch():
            return self.provider.get_cpi(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return CPIResponse(
            data_type="cpi",
            data=items,
            count=len(items),
        )

    async def get_exchange_rate(self, limit: int = 20) -> ExchangeRateResponse:
        """Get USD/VND exchange rate data."""
        def _fetch():
            return self.provider.get_exchange_rate(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return ExchangeRateResponse(
            data_type="exchange_rate",
            data=items,
            count=len(items),
        )

    async def get_import_export(self, limit: int = 20) -> ImportExportResponse:
        """Get import/export trade data."""
        def _fetch():
            return self.provider.get_import_export(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return ImportExportResponse(
            data_type="import_export",
            data=items,
            count=len(items),
        )

    async def get_fdi(self, limit: int = 20) -> FDIResponse:
        """Get FDI (Foreign Direct Investment) data."""
        def _fetch():
            return self.provider.get_fdi(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return FDIResponse(
            data_type="fdi",
            data=items,
            count=len(items),
        )

    async def get_money_supply(self, limit: int = 20) -> MoneySupplyResponse:
        """Get money supply M2 data."""
        def _fetch():
            return self.provider.get_money_supply(limit=limit)

        data = await run_sync(_fetch)
        items = self._convert_to_items(data)
        return MoneySupplyResponse(
            data_type="money_supply",
            data=items,
            count=len(items),
        )
