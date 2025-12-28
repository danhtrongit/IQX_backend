"""Service dependencies."""
from app.application.symbol.services import SymbolService
from app.application.quote.services import QuoteService
from app.application.financial.services import FinancialService, CompanyService
from app.application.insight.services import InsightService, TradingInsightService

from app.infrastructure.vnstock.quote_provider import VnstockQuoteProvider
from app.infrastructure.vnstock.financial_provider import (
    VnstockFinancialProvider,
    VnstockCompanyProvider,
)
from app.infrastructure.vnstock.insight_provider import (
    VnstockInsightProvider,
    VnstockTradingInsightProvider,
)
from app.infrastructure.repositories.symbol_repo import (
    SQLAlchemySymbolRepository,
    SQLAlchemyIndustryRepository,
)
from app.presentation.deps.db_deps import get_db


async def get_symbol_service():
    """Get symbol service."""
    async for session in get_db():
        symbol_repo = SQLAlchemySymbolRepository(session)
        industry_repo = SQLAlchemyIndustryRepository(session)
        return SymbolService(symbol_repo, industry_repo)


def get_quote_service() -> QuoteService:
    """Get quote service."""
    provider = VnstockQuoteProvider()
    return QuoteService(data_provider=provider)


def get_financial_service() -> FinancialService:
    """Get financial service."""
    provider = VnstockFinancialProvider()
    return FinancialService(data_provider=provider)


def get_company_service() -> CompanyService:
    """Get company service."""
    provider = VnstockCompanyProvider()
    return CompanyService(data_provider=provider)


def get_insight_service() -> InsightService:
    """Get insight service."""
    provider = VnstockInsightProvider()
    return InsightService(data_provider=provider)


def get_trading_insight_service() -> TradingInsightService:
    """Get trading insight service."""
    provider = VnstockTradingInsightProvider()
    return TradingInsightService(data_provider=provider)
