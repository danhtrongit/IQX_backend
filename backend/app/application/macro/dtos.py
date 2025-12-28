"""Macro DTOs for Vietnamese macroeconomic data."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class MacroDataItem(BaseModel):
    """Individual macro data item from vnstock_data Macro API."""

    report_time: Optional[str] = Field(None, description="Report time/period")
    group_name: Optional[str] = Field(None, description="Category group name")
    name: Optional[str] = Field(None, description="Indicator name")
    value: Optional[float] = Field(None, description="Indicator value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    source: Optional[str] = Field(None, description="Data source")
    report_type: Optional[str] = Field(None, description="Report type (monthly, quarterly, yearly)")

    class Config:
        extra = "allow"  # Allow extra fields from vnstock_data


class MacroResponse(BaseModel):
    """Response model for macro data endpoints."""

    data_type: str = Field(..., description="Type of macro data (gdp, cpi, exchange_rate, etc.)")
    data: List[MacroDataItem] = Field(default_factory=list, description="List of macro data items")
    count: int = Field(..., description="Number of items returned")


class GDPResponse(MacroResponse):
    """GDP specific response."""
    data_type: str = "gdp"


class CPIResponse(MacroResponse):
    """CPI specific response."""
    data_type: str = "cpi"


class ExchangeRateResponse(MacroResponse):
    """Exchange rate specific response."""
    data_type: str = "exchange_rate"


class ImportExportResponse(MacroResponse):
    """Import/Export trade data response."""
    data_type: str = "import_export"


class FDIResponse(MacroResponse):
    """Foreign Direct Investment response."""
    data_type: str = "fdi"


class MoneySupplyResponse(MacroResponse):
    """Money supply M2 response."""
    data_type: str = "money_supply"
