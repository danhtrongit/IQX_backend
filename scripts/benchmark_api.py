"""Comprehensive benchmark script for API performance testing."""
import asyncio
import time
from app.application.market.services import MarketService
from app.application.quote.services import QuoteService
from app.application.quote.dtos import PriceBoardRequest, HistoryRequest
from app.infrastructure.vnstock.quote_provider import VnstockQuoteProvider
from app.application.listing.services import ListingService
from app.infrastructure.vnstock.listing_provider import VnstockListingProvider
from app.application.insight.services import InsightService
from app.infrastructure.vnstock.insight_provider import VnstockInsightProvider
from app.core.async_utils import run_sync


async def benchmark(name: str, func, runs: int = 3):
    """Run benchmark for a function."""
    print(f"\n{name}")
    print("-" * 40)
    
    # Warm up
    try:
        if asyncio.iscoroutinefunction(func):
            await func()
        else:
            await run_sync(func)
    except Exception as e:
        print(f"  Warm-up error: {e}")
        return None
    
    # Benchmark
    times = []
    for i in range(runs):
        start = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func()
            else:
                result = await run_sync(func)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            
            # Get result info
            if hasattr(result, 'count'):
                info = f"{result.count} items"
            elif hasattr(result, 'indices'):
                info = f"{len(result.indices)} indices"
            elif hasattr(result, 'data'):
                info = f"{len(result.data)} items"
            else:
                info = "OK"
            
            print(f"  Run {i+1}: {elapsed:.3f}s - {info}")
        except Exception as e:
            print(f"  Run {i+1}: ERROR - {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"  Average: {avg:.3f}s")
        return avg
    return None


async def main():
    print("=" * 60)
    print("API Performance Benchmark (vnstock_data + async optimization)")
    print("=" * 60)
    
    results = {}
    
    # 1. Market Overview
    market_service = MarketService()
    results['market_overview'] = await benchmark(
        "1. Market Overview (/v1/market/overview)",
        market_service.get_market_overview
    )
    
    # 2. Price Board
    quote_provider = VnstockQuoteProvider()
    quote_service = QuoteService(data_provider=quote_provider)
    symbols = ["VNM", "FPT", "VCB", "HPG", "MWG"]
    request = PriceBoardRequest(symbols=symbols)
    results['price_board'] = await benchmark(
        "2. Price Board (/v1/quotes/price-board) - 5 symbols",
        lambda: quote_service.get_price_board(request)
    )
    
    # 3. History
    history_request = HistoryRequest(start="2024-01-01", end="2024-12-20", interval="1D")
    results['history'] = await benchmark(
        "3. History (/v1/quotes/{symbol}/history)",
        lambda: quote_service.get_history("VCB", history_request)
    )
    
    # 4. Listing Stocks
    listing_provider = VnstockListingProvider()
    listing_service = ListingService(data_provider=listing_provider)
    results['listing'] = await benchmark(
        "4. Listing Stocks (/v1/listing/stocks)",
        listing_service.get_stocks
    )
    
    # 5. Top Gainer
    insight_provider = VnstockInsightProvider()
    insight_service = InsightService(data_provider=insight_provider)
    results['top_gainer'] = await benchmark(
        "5. Top Gainer (/v1/insight/top/gainer)",
        lambda: insight_service.get_top_gainer(index="VNINDEX", limit=10)
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, avg in results.items():
        if avg:
            status = "✅" if avg < 1.0 else "⚠️" if avg < 2.0 else "❌"
            print(f"  {status} {name}: {avg:.3f}s")
        else:
            print(f"  ❌ {name}: FAILED")
    
    print("\n" + "=" * 60)
    print("Benchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())
