"""Script to sync symbols from vnstock."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.db.session import async_session_factory, init_db
from app.infrastructure.repositories.symbol_repo import (
    SQLAlchemySymbolRepository,
    SQLAlchemyIndustryRepository,
)
from app.infrastructure.vnstock.provider import VnstockProvider
from app.application.symbol.services import SymbolService


async def sync_symbols(source: str = "vci", sync_details: bool = False):
    """Sync symbols from vnstock."""
    print(f"Initializing database...")
    await init_db()
    
    async with async_session_factory() as session:
        symbol_repo = SQLAlchemySymbolRepository(session)
        industry_repo = SQLAlchemyIndustryRepository(session)
        
        service = SymbolService(
            symbol_repo=symbol_repo,
            industry_repo=industry_repo,
        )
        
        provider = VnstockProvider(source=source)
        
        print(f"Syncing symbols from {source}...")
        print(f"Sync details: {sync_details}")
        
        result = await service.sync_from_vnstock(
            data_provider=provider,
            sync_details=sync_details,
        )
        
        await session.commit()
        
        print(f"\n{result.message}")
        print(f"Total symbols synced: {result.synced_count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync symbols from vnstock")
    parser.add_argument(
        "--source",
        type=str,
        default="vci",
        choices=["vci", "vnd"],
        help="Data source (default: vci)",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Also sync company details (slower)",
    )
    
    args = parser.parse_args()
    
    asyncio.run(sync_symbols(source=args.source, sync_details=args.details))
