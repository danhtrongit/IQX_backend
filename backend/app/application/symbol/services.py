"""Symbol application services."""
from typing import Optional, List, Protocol
from decimal import Decimal

from app.domain.symbol.entities import Symbol, Industry
from app.domain.symbol.repositories import SymbolRepository, IndustryRepository
from app.domain.symbol.errors import SymbolNotFoundError
from app.application.symbol.dtos import (
    SymbolListRequest,
    SymbolSearchRequest,
    SymbolResponse,
    SymbolDetailResponse,
    SymbolListResponse,
    IndustryResponse,
    IndustryListResponse,
    SyncResultResponse,
)


class VnstockDataProvider(Protocol):
    """Vnstock data provider interface."""
    
    def get_all_symbols(self) -> List[dict]:
        """Get all symbols from vnstock."""
        ...
    
    def get_symbols_by_industries(self) -> List[dict]:
        """Get symbols with industry info."""
        ...
    
    def get_industries_icb(self) -> List[dict]:
        """Get ICB industries."""
        ...
    
    def get_company_overview(self, symbol: str) -> Optional[dict]:
        """Get company overview."""
        ...


class SymbolService:
    """Symbol service."""
    
    def __init__(
        self,
        symbol_repo: SymbolRepository,
        industry_repo: IndustryRepository,
    ):
        self.symbol_repo = symbol_repo
        self.industry_repo = industry_repo
    
    async def get_symbol(self, symbol: str) -> SymbolDetailResponse:
        """Get symbol detail by ticker code."""
        entity = await self.symbol_repo.get_by_symbol(symbol.upper())
        if not entity:
            raise SymbolNotFoundError(symbol)
        return self._to_detail_response(entity)
    
    async def get_symbol_by_id(self, symbol_id: int) -> SymbolDetailResponse:
        """Get symbol detail by ID."""
        entity = await self.symbol_repo.get_by_id(symbol_id)
        if not entity:
            raise SymbolNotFoundError(symbol_id)
        return self._to_detail_response(entity)
    
    async def list_symbols(self, request: SymbolListRequest) -> SymbolListResponse:
        """List symbols with filters."""
        symbols = await self.symbol_repo.get_all(
            exchange=request.exchange,
            type=request.type,
            icb_code2=request.icb_code2,
            is_active=request.is_active,
            limit=request.limit,
            offset=request.offset,
        )
        total = await self.symbol_repo.count(
            exchange=request.exchange,
            type=request.type,
            icb_code2=request.icb_code2,
            is_active=request.is_active,
        )
        return SymbolListResponse(
            items=[self._to_response(s) for s in symbols],
            total=total,
            limit=request.limit,
            offset=request.offset,
        )
    
    async def search_symbols(self, request: SymbolSearchRequest) -> List[SymbolResponse]:
        """Search symbols by name or code."""
        symbols = await self.symbol_repo.search(
            query=request.query,
            limit=request.limit,
        )
        return [self._to_response(s) for s in symbols]
    
    async def list_industries(self, level: Optional[int] = None) -> IndustryListResponse:
        """List industries."""
        industries = await self.industry_repo.get_all(level=level)
        return IndustryListResponse(
            items=[self._to_industry_response(i) for i in industries],
            total=len(industries),
        )
    
    async def sync_from_vnstock(
        self,
        data_provider: VnstockDataProvider,
        sync_details: bool = False,
    ) -> SyncResultResponse:
        """Sync symbols from vnstock data source."""
        # Get symbols with exchange info
        exchange_data = data_provider.get_all_symbols()
        
        # Get symbols with industry info
        industry_data = data_provider.get_symbols_by_industries()
        
        # Create industry lookup
        industry_map = {item.get("symbol"): item for item in industry_data}
        
        # Sync industries first
        icb_data = data_provider.get_industries_icb()
        industries = [
            Industry(
                id=0,
                icb_code=item.get("icb_code", ""),
                icb_name=item.get("icb_name", ""),
                en_icb_name=item.get("en_icb_name"),
                level=item.get("level", 1),
            )
            for item in icb_data
        ]
        await self.industry_repo.bulk_upsert(industries)
        
        # Build symbols
        symbols = []
        for item in exchange_data:
            symbol_code = item.get("symbol", "")
            ind = industry_map.get(symbol_code, {})
            
            symbol = Symbol(
                id=0,
                symbol=symbol_code,
                organ_name=item.get("organ_name"),
                en_organ_name=item.get("en_organ_name"),
                organ_short_name=item.get("organ_short_name"),
                exchange=item.get("exchange"),
                type=item.get("type"),
                icb_code1=ind.get("icb_code1"),
                icb_code2=ind.get("icb_code2"),
                icb_code3=ind.get("icb_code3"),
                icb_code4=ind.get("icb_code4"),
                icb_name2=ind.get("icb_name2"),
                icb_name3=ind.get("icb_name3"),
                icb_name4=ind.get("icb_name4"),
            )
            
            # Optionally sync company details (slower)
            if sync_details and item.get("type") == "STOCK":
                try:
                    overview = data_provider.get_company_overview(symbol_code)
                    if overview:
                        symbol.company_profile = overview.get("company_profile")
                        symbol.history = overview.get("history")
                        symbol.issue_share = self._to_decimal(overview.get("issue_share"))
                        symbol.charter_capital = self._to_decimal(overview.get("charter_capital"))
                except Exception:
                    pass  # Skip if company detail fails
            
            symbols.append(symbol)
        
        # Bulk upsert
        count = await self.symbol_repo.bulk_upsert(symbols)
        
        return SyncResultResponse(
            synced_count=count,
            message=f"Successfully synced {count} symbols",
        )
    
    @staticmethod
    def _to_decimal(value) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None
    
    @staticmethod
    def _to_response(entity: Symbol) -> SymbolResponse:
        return SymbolResponse(
            id=entity.id,
            symbol=entity.symbol,
            organ_name=entity.organ_name,
            en_organ_name=entity.en_organ_name,
            organ_short_name=entity.organ_short_name,
            exchange=entity.exchange,
            type=entity.type,
            icb_code2=entity.icb_code2,
            icb_code3=entity.icb_code3,
            icb_code4=entity.icb_code4,
            icb_name2=entity.icb_name2,
            icb_name3=entity.icb_name3,
            icb_name4=entity.icb_name4,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def _to_detail_response(entity: Symbol) -> SymbolDetailResponse:
        return SymbolDetailResponse(
            id=entity.id,
            symbol=entity.symbol,
            organ_name=entity.organ_name,
            en_organ_name=entity.en_organ_name,
            organ_short_name=entity.organ_short_name,
            exchange=entity.exchange,
            type=entity.type,
            icb_code1=entity.icb_code1,
            icb_code2=entity.icb_code2,
            icb_code3=entity.icb_code3,
            icb_code4=entity.icb_code4,
            icb_name2=entity.icb_name2,
            icb_name3=entity.icb_name3,
            icb_name4=entity.icb_name4,
            company_profile=entity.company_profile,
            history=entity.history,
            issue_share=entity.issue_share,
            charter_capital=entity.charter_capital,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def _to_industry_response(entity: Industry) -> IndustryResponse:
        return IndustryResponse(
            id=entity.id,
            icb_code=entity.icb_code,
            icb_name=entity.icb_name,
            en_icb_name=entity.en_icb_name,
            level=entity.level,
            parent_code=entity.parent_code,
        )
