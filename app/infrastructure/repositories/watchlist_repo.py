"""Watchlist repository implementation."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.watchlist.entities import WatchlistItem
from app.infrastructure.models.watchlist_model import WatchlistModel


class SQLAlchemyWatchlistRepository:
    """SQLAlchemy implementation of WatchlistRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, item_id: int) -> Optional[WatchlistItem]:
        result = await self.session.execute(
            select(WatchlistModel).where(WatchlistModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_symbol(
        self, user_id: int, symbol: str
    ) -> Optional[WatchlistItem]:
        result = await self.session.execute(
            select(WatchlistModel).where(
                WatchlistModel.user_id == user_id,
                WatchlistModel.symbol == symbol.upper(),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_user(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[WatchlistItem]:
        result = await self.session.execute(
            select(WatchlistModel)
            .where(WatchlistModel.user_id == user_id)
            .order_by(WatchlistModel.position, WatchlistModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(WatchlistModel.id)).where(
                WatchlistModel.user_id == user_id
            )
        )
        return result.scalar_one()

    async def create(
        self,
        user_id: int,
        symbol: str,
        notes: Optional[str] = None,
        target_price: Optional[float] = None,
        alert_enabled: bool = False,
    ) -> WatchlistItem:
        # Get max position for user
        result = await self.session.execute(
            select(func.coalesce(func.max(WatchlistModel.position), 0)).where(
                WatchlistModel.user_id == user_id
            )
        )
        max_position = result.scalar_one()

        model = WatchlistModel(
            user_id=user_id,
            symbol=symbol.upper(),
            notes=notes,
            target_price=target_price,
            alert_enabled=alert_enabled,
            position=max_position + 1,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(
        self,
        item_id: int,
        notes: Optional[str] = None,
        target_price: Optional[float] = None,
        alert_enabled: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> Optional[WatchlistItem]:
        # Build update values
        values = {"updated_at": datetime.utcnow()}
        if notes is not None:
            values["notes"] = notes
        if target_price is not None:
            values["target_price"] = target_price
        if alert_enabled is not None:
            values["alert_enabled"] = alert_enabled
        if position is not None:
            values["position"] = position

        await self.session.execute(
            update(WatchlistModel)
            .where(WatchlistModel.id == item_id)
            .values(**values)
        )
        return await self.get_by_id(item_id)

    async def delete(self, item_id: int) -> bool:
        result = await self.session.execute(
            delete(WatchlistModel).where(WatchlistModel.id == item_id)
        )
        return result.rowcount > 0

    async def delete_by_user_and_symbol(self, user_id: int, symbol: str) -> bool:
        result = await self.session.execute(
            delete(WatchlistModel).where(
                WatchlistModel.user_id == user_id,
                WatchlistModel.symbol == symbol.upper(),
            )
        )
        return result.rowcount > 0

    async def exists(self, user_id: int, symbol: str) -> bool:
        result = await self.session.execute(
            select(WatchlistModel.id).where(
                WatchlistModel.user_id == user_id,
                WatchlistModel.symbol == symbol.upper(),
            )
        )
        return result.scalar_one_or_none() is not None

    async def bulk_create(
        self, user_id: int, symbols: list[str]
    ) -> list[WatchlistItem]:
        # Get max position
        result = await self.session.execute(
            select(func.coalesce(func.max(WatchlistModel.position), 0)).where(
                WatchlistModel.user_id == user_id
            )
        )
        max_position = result.scalar_one()

        # Get existing symbols
        existing_result = await self.session.execute(
            select(WatchlistModel.symbol).where(
                WatchlistModel.user_id == user_id,
                WatchlistModel.symbol.in_([s.upper() for s in symbols]),
            )
        )
        existing_symbols = {row[0] for row in existing_result.fetchall()}

        # Create new items
        items = []
        for i, symbol in enumerate(symbols):
            upper_symbol = symbol.upper()
            if upper_symbol not in existing_symbols:
                model = WatchlistModel(
                    user_id=user_id,
                    symbol=upper_symbol,
                    position=max_position + i + 1,
                )
                self.session.add(model)
                items.append(model)

        await self.session.flush()
        for item in items:
            await self.session.refresh(item)

        return [self._to_entity(m) for m in items]

    async def reorder(
        self, user_id: int, item_positions: list[tuple[int, int]]
    ) -> None:
        for item_id, position in item_positions:
            await self.session.execute(
                update(WatchlistModel)
                .where(
                    WatchlistModel.id == item_id,
                    WatchlistModel.user_id == user_id,
                )
                .values(position=position, updated_at=datetime.utcnow())
            )

    @staticmethod
    def _to_entity(model: WatchlistModel) -> WatchlistItem:
        return WatchlistItem(
            id=model.id,
            user_id=model.user_id,
            symbol=model.symbol,
            notes=model.notes,
            target_price=model.target_price,
            alert_enabled=model.alert_enabled,
            position=model.position,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
