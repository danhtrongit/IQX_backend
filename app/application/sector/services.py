"""Sector service layer with caching."""

from typing import Optional, List, Dict, Any

from app.core.cache import cached, CacheTTL
from app.core.logging import get_logger
from app.infrastructure.vietcap.sector_provider import VietcapSectorProvider

from .schemas import (
    SectorInfoResponse,
    SectorListResponse,
    SectorRanking,
    SectorRankingValue,
    SectorRankingResponse,
    SectorCompany,
    SectorCompaniesResponse,
    SectorIndexDataPoint,
    SectorIndexHistory,
    TradingDatesResponse,
    ICBCodeItem,
)

logger = get_logger(__name__)


class SectorService:
    """Service for sector data with caching."""

    def __init__(self):
        self.provider = VietcapSectorProvider()
        self._icb_cache: Dict[int, Dict[str, str]] = {}

    async def _get_icb_mapping(self) -> Dict[int, Dict[str, str]]:
        """Get ICB codes mapping (cached internally)."""
        if not self._icb_cache:
            icb_codes = await self.provider.get_icb_codes()
            if icb_codes:
                for item in icb_codes:
                    code = item.get("name")
                    if code:
                        self._icb_cache[code] = {
                            "en_sector": item.get("enSector"),
                            "vi_sector": item.get("viSector"),
                            "icb_level": item.get("icbLevel"),
                        }
        return self._icb_cache

    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @cached("sector:information", ttl=CacheTTL.INDUSTRIES)
    async def get_sector_information(
        self,
        icb_level: int = 2
    ) -> SectorListResponse:
        """
        Get sector information with performance metrics.
        
        Args:
            icb_level: ICB level (1-4), default 2 (supersector)
            
        Returns:
            SectorListResponse with all sectors
        """
        data = await self.provider.get_sector_information(icb_level)
        icb_mapping = await self._get_icb_mapping()
        
        sectors = []
        if data:
            for item in data:
                icb_code = item.get("icbCode")
                mapping = icb_mapping.get(icb_code, {})
                
                sectors.append(SectorInfoResponse(
                    icb_code=icb_code,
                    en_sector=mapping.get("en_sector"),
                    vi_sector=mapping.get("vi_sector"),
                    icb_level=icb_level,
                    market_cap=self._safe_float(item.get("marketCap")),
                    weight_percent=self._safe_float(item.get("weightPercent")),
                    last_close_index=self._safe_float(item.get("lastCloseIndex")),
                    last_20_day_index=item.get("last20DayIndex"),
                    percent_change_1d=self._safe_float(item.get("percentPriceChange1Day")),
                    percent_change_1w=self._safe_float(item.get("percentPriceChange1Week")),
                    percent_change_1m=self._safe_float(item.get("percentPriceChange1Month")),
                    percent_change_6m=self._safe_float(item.get("percentPriceChange6Month")),
                    percent_change_ytd=self._safe_float(item.get("percentPriceChangeYTD")),
                    percent_change_1y=self._safe_float(item.get("percentPriceChange1Year")),
                    percent_change_2y=self._safe_float(item.get("percentPriceChange2Year")),
                    percent_change_5y=self._safe_float(item.get("percentPriceChange5Year")),
                ))
        
        return SectorListResponse(
            total=len(sectors),
            icb_level=icb_level,
            sectors=sectors
        )

    @cached("sector:ranking", ttl=CacheTTL.TOP_STOCKS)
    async def get_sector_ranking(
        self,
        icb_level: int = 2,
        adtv: int = 3,
        value: int = 3
    ) -> SectorRankingResponse:
        """
        Get sector ranking with daily trends.
        
        Args:
            icb_level: ICB level (1-4)
            adtv: ADTV filter
            value: Value filter
            
        Returns:
            SectorRankingResponse with rankings
        """
        data = await self.provider.get_sector_ranking(icb_level, adtv, value)
        icb_mapping = await self._get_icb_mapping()
        
        rankings = []
        if data:
            for item in data:
                icb_code = item.get("name")  # 'name' contains ICB code
                mapping = icb_mapping.get(icb_code, {})
                
                values = []
                for v in item.get("values", []):
                    values.append(SectorRankingValue(
                        date=v.get("date", ""),
                        value=self._safe_float(v.get("value")),
                        sector_trend=v.get("sectorTrend")
                    ))
                
                rankings.append(SectorRanking(
                    icb_code=icb_code,
                    en_sector=mapping.get("en_sector"),
                    vi_sector=mapping.get("vi_sector"),
                    values=values
                ))
        
        return SectorRankingResponse(
            total=len(rankings),
            icb_level=icb_level,
            rankings=rankings
        )

    @cached("sector:companies", ttl=CacheTTL.INDUSTRIES)
    async def get_sector_companies(
        self,
        icb_code: int
    ) -> SectorCompaniesResponse:
        """
        Get companies within a sector.
        
        Args:
            icb_code: ICB sector code
            
        Returns:
            SectorCompaniesResponse with company list
        """
        data = await self.provider.get_sector_companies(icb_code)
        icb_mapping = await self._get_icb_mapping()
        mapping = icb_mapping.get(icb_code, {})
        
        companies = []
        if data:
            for item in data:
                companies.append(SectorCompany(
                    ticker=item.get("ticker", ""),
                    company_name=item.get("organShortNameVi"),
                    market_cap=self._safe_float(item.get("marketCap")),
                    latest_price=self._safe_float(item.get("latestPrice")),
                    percent_change=self._safe_float(item.get("percentPriceChange")),
                    ttm_pe=self._safe_float(item.get("ttmPe")),
                    ttm_pb=self._safe_float(item.get("ttmPb")),
                    ttm_eps=self._safe_float(item.get("ttmEps")),
                    roe=self._safe_float(item.get("roe")),
                    roa=self._safe_float(item.get("roa")),
                    avg_volume_1m=self._safe_float(item.get("averageMatchVolume1Month")),
                    foreign_room=self._safe_float(item.get("foreignRoom")),
                    foreign_ownership=self._safe_float(item.get("foreignOwnership")),
                ))
        
        return SectorCompaniesResponse(
            icb_code=icb_code,
            en_sector=mapping.get("en_sector"),
            vi_sector=mapping.get("vi_sector"),
            total_companies=len(companies),
            companies=companies
        )

    @cached("sector:index-history", ttl=CacheTTL.HISTORICAL_RECENT)
    async def get_sector_index_history(
        self,
        icb_codes: List[int],
        icb_level: int = 2,
        number_of_days: str = "ALL"
    ) -> List[SectorIndexHistory]:
        """
        Get sector index history for charting.
        
        Args:
            icb_codes: List of ICB codes
            icb_level: ICB level
            number_of_days: Number of days or "ALL"
            
        Returns:
            List of SectorIndexHistory
        """
        data = await self.provider.get_sector_index_history(
            icb_codes, icb_level, number_of_days
        )
        icb_mapping = await self._get_icb_mapping()
        
        result = []
        if data:
            for item in data:
                icb_code = item.get("icbCode")
                mapping = icb_mapping.get(icb_code, {})
                
                data_points = []
                for point in item.get("data", []):
                    data_points.append(SectorIndexDataPoint(
                        date=point.get("date", ""),
                        value=self._safe_float(point.get("value"))
                    ))
                
                result.append(SectorIndexHistory(
                    icb_code=icb_code,
                    en_sector=mapping.get("en_sector"),
                    vi_sector=mapping.get("vi_sector"),
                    data=data_points
                ))
        
        return result

    @cached("sector:trading-dates", ttl=CacheTTL.INTRADAY)
    async def get_trading_dates(self) -> TradingDatesResponse:
        """
        Get recent trading dates.
        
        Returns:
            TradingDatesResponse with date list
        """
        data = await self.provider.get_trading_dates()
        return TradingDatesResponse(dates=data or [])

    @cached("sector:icb-codes", ttl=CacheTTL.INDUSTRIES)
    async def get_icb_codes(self) -> List[ICBCodeItem]:
        """
        Get all ICB codes with names.
        
        Returns:
            List of ICBCodeItem
        """
        data = await self.provider.get_icb_codes()
        
        result = []
        if data:
            for item in data:
                result.append(ICBCodeItem(
                    code=item.get("name"),
                    en_sector=item.get("enSector"),
                    vi_sector=item.get("viSector"),
                    icb_level=item.get("icbLevel"),
                    is_level1_custom=item.get("isLevel1Custom"),
                ))
        
        return result


# Singleton service instance
_sector_service: Optional[SectorService] = None


def get_sector_service() -> SectorService:
    """Get or create sector service instance."""
    global _sector_service
    if _sector_service is None:
        _sector_service = SectorService()
    return _sector_service
