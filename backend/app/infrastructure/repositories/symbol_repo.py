"""Symbol repository implementations."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, func, or_, case
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.symbol.entities import Symbol, Industry
from app.infrastructure.models.symbol_model import SymbolModel, IndustryModel


class SQLAlchemySymbolRepository:
    """SQLAlchemy implementation of SymbolRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, symbol_id: int) -> Optional[Symbol]:
        result = await self.session.execute(
            select(SymbolModel).where(SymbolModel.id == symbol_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_by_symbol(self, symbol: str) -> Optional[Symbol]:
        result = await self.session.execute(
            select(SymbolModel).where(SymbolModel.symbol == symbol.upper())
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_all(
        self,
        exchange: Optional[str] = None,
        type: Optional[str] = None,
        icb_code2: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Symbol]:
        query = select(SymbolModel)
        
        if exchange:
            query = query.where(SymbolModel.exchange == exchange)
        if type:
            query = query.where(SymbolModel.type == type)
        if icb_code2:
            query = query.where(SymbolModel.icb_code2 == icb_code2)
        if is_active is not None:
            query = query.where(SymbolModel.is_active == is_active)
        
        query = query.order_by(SymbolModel.symbol).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
    
    async def count(
        self,
        exchange: Optional[str] = None,
        type: Optional[str] = None,
        icb_code2: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> int:
        query = select(func.count(SymbolModel.id))
        
        if exchange:
            query = query.where(SymbolModel.exchange == exchange)
        if type:
            query = query.where(SymbolModel.type == type)
        if icb_code2:
            query = query.where(SymbolModel.icb_code2 == icb_code2)
        if is_active is not None:
            query = query.where(SymbolModel.is_active == is_active)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def search(self, query: str, limit: int = 20) -> List[Symbol]:
        search_pattern = f"%{query}%"
        query_upper = query.upper()
        starts_with_pattern = f"{query}%"
        
        # Priority ordering: exact symbol match > starts with > contains
        priority = case(
            (func.upper(SymbolModel.symbol) == query_upper, 0),  # Exact match
            (SymbolModel.symbol.ilike(starts_with_pattern), 1),  # Starts with
            (SymbolModel.organ_name.ilike(starts_with_pattern), 2),  # Name starts with
            else_=3  # Contains
        )
        
        stmt = (
            select(SymbolModel)
            .where(
                or_(
                    SymbolModel.symbol.ilike(search_pattern),
                    SymbolModel.organ_name.ilike(search_pattern),
                    SymbolModel.en_organ_name.ilike(search_pattern),
                )
            )
            .where(SymbolModel.is_active == True)
            .order_by(priority, SymbolModel.symbol)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
    
    async def create(self, symbol: Symbol) -> Symbol:
        model = self._to_model(symbol)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)
    
    async def update(self, symbol: Symbol) -> Symbol:
        await self.session.execute(
            update(SymbolModel)
            .where(SymbolModel.id == symbol.id)
            .values(
                organ_name=symbol.organ_name,
                en_organ_name=symbol.en_organ_name,
                organ_short_name=symbol.organ_short_name,
                exchange=symbol.exchange,
                type=symbol.type,
                icb_code1=symbol.icb_code1,
                icb_code2=symbol.icb_code2,
                icb_code3=symbol.icb_code3,
                icb_code4=symbol.icb_code4,
                icb_name2=symbol.icb_name2,
                icb_name3=symbol.icb_name3,
                icb_name4=symbol.icb_name4,
                company_profile=symbol.company_profile,
                history=symbol.history,
                issue_share=symbol.issue_share,
                charter_capital=symbol.charter_capital,
                is_active=symbol.is_active,
                updated_at=datetime.utcnow(),
            )
        )
        return await self.get_by_id(symbol.id)
    
    async def upsert(self, symbol: Symbol) -> Symbol:
        existing = await self.get_by_symbol(symbol.symbol)
        if existing:
            symbol.id = existing.id
            return await self.update(symbol)
        return await self.create(symbol)
    
    async def bulk_upsert(self, symbols: List[Symbol]) -> int:
        if not symbols:
            return 0
        
        for symbol in symbols:
            stmt = insert(SymbolModel).values(
                symbol=symbol.symbol,
                organ_name=symbol.organ_name,
                en_organ_name=symbol.en_organ_name,
                organ_short_name=symbol.organ_short_name,
                exchange=symbol.exchange,
                type=symbol.type,
                icb_code1=symbol.icb_code1,
                icb_code2=symbol.icb_code2,
                icb_code3=symbol.icb_code3,
                icb_code4=symbol.icb_code4,
                icb_name2=symbol.icb_name2,
                icb_name3=symbol.icb_name3,
                icb_name4=symbol.icb_name4,
                company_profile=symbol.company_profile,
                history=symbol.history,
                issue_share=symbol.issue_share,
                charter_capital=symbol.charter_capital,
                is_active=symbol.is_active,
            )
            stmt = stmt.on_duplicate_key_update(
                organ_name=stmt.inserted.organ_name,
                en_organ_name=stmt.inserted.en_organ_name,
                organ_short_name=stmt.inserted.organ_short_name,
                exchange=stmt.inserted.exchange,
                type=stmt.inserted.type,
                icb_code1=stmt.inserted.icb_code1,
                icb_code2=stmt.inserted.icb_code2,
                icb_code3=stmt.inserted.icb_code3,
                icb_code4=stmt.inserted.icb_code4,
                icb_name2=stmt.inserted.icb_name2,
                icb_name3=stmt.inserted.icb_name3,
                icb_name4=stmt.inserted.icb_name4,
                company_profile=stmt.inserted.company_profile,
                history=stmt.inserted.history,
                issue_share=stmt.inserted.issue_share,
                charter_capital=stmt.inserted.charter_capital,
                updated_at=func.now(),
            )
            await self.session.execute(stmt)
        
        await self.session.flush()
        return len(symbols)
    
    async def symbol_exists(self, symbol: str) -> bool:
        result = await self.session.execute(
            select(SymbolModel.id).where(SymbolModel.symbol == symbol.upper())
        )
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    def _to_entity(model: SymbolModel) -> Symbol:
        return Symbol(
            id=model.id,
            symbol=model.symbol,
            organ_name=model.organ_name,
            en_organ_name=model.en_organ_name,
            organ_short_name=model.organ_short_name,
            exchange=model.exchange,
            type=model.type,
            icb_code1=model.icb_code1,
            icb_code2=model.icb_code2,
            icb_code3=model.icb_code3,
            icb_code4=model.icb_code4,
            icb_name2=model.icb_name2,
            icb_name3=model.icb_name3,
            icb_name4=model.icb_name4,
            company_profile=model.company_profile,
            history=model.history,
            issue_share=model.issue_share,
            charter_capital=model.charter_capital,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def _to_model(entity: Symbol) -> SymbolModel:
        return SymbolModel(
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
        )


class SQLAlchemyIndustryRepository:
    """SQLAlchemy implementation of IndustryRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_code(self, icb_code: str) -> Optional[Industry]:
        result = await self.session.execute(
            select(IndustryModel).where(IndustryModel.icb_code == icb_code)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_all(self, level: Optional[int] = None) -> List[Industry]:
        query = select(IndustryModel)
        if level is not None:
            query = query.where(IndustryModel.level == level)
        query = query.order_by(IndustryModel.icb_code)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
    
    async def bulk_upsert(self, industries: List[Industry]) -> int:
        if not industries:
            return 0
        
        for industry in industries:
            stmt = insert(IndustryModel).values(
                icb_code=industry.icb_code,
                icb_name=industry.icb_name,
                en_icb_name=industry.en_icb_name,
                level=industry.level,
                parent_code=industry.parent_code,
            )
            stmt = stmt.on_duplicate_key_update(
                icb_name=stmt.inserted.icb_name,
                en_icb_name=stmt.inserted.en_icb_name,
                level=stmt.inserted.level,
                parent_code=stmt.inserted.parent_code,
            )
            await self.session.execute(stmt)
        
        await self.session.flush()
        return len(industries)
    
    @staticmethod
    def _to_entity(model: IndustryModel) -> Industry:
        return Industry(
            id=model.id,
            icb_code=model.icb_code,
            icb_name=model.icb_name,
            en_icb_name=model.en_icb_name,
            level=model.level,
            parent_code=model.parent_code,
            created_at=model.created_at,
        )
