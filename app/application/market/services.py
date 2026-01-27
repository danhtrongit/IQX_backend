"""Market application services."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.core.logging import get_logger
from app.core.async_utils import run_sync, run_parallel
from app.application.market.dtos import (
    IndexResponse,
    MarketOverviewResponse,
    IndexHistoryRequest,
    IndexHistoryItem,
    IndexHistoryResponse,
    MarketEvaluationResponse,
    MarketEvaluationItem,
    AllocatedValueResponse
)
from app.infrastructure.vnstock.instance_cache import get_quote, get_market
from app.infrastructure.vietcap.allocated_value_provider import VietcapAllocatedValueProvider

logger = get_logger(__name__)

# Index codes
INDEX_CODES = ["VNINDEX", "HNXINDEX", "UPCOMINDEX", "VN30"]


def _fetch_index_sync(index_code: str) -> Optional[Dict]:
    """Sync function to fetch single index data."""
    try:
        quote = get_quote(index_code)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        df = quote.history(
            start=start_date,
            end=end_date,
            interval="1D",
            count_back=2,
        )
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        close_val = float(latest.get("close", 0))
        prev_close = float(prev.get("close", close_val))
        change = close_val - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return {
            "index_code": index_code,
            "index_value": close_val,
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "ref_value": prev_close,
            "open_value": float(latest.get("open", 0)),
            "high_value": float(latest.get("high", 0)),
            "low_value": float(latest.get("low", 0)),
            "total_volume": int(latest.get("volume", 0)),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Error fetching index {index_code}: {e}")
        return None


class MarketService:
    """Market service for index and market overview data."""
    
    async def get_market_overview(self) -> MarketOverviewResponse:
        """
        Get market overview with all major indices.
        Fetches all indices in PARALLEL for better performance.
        """
        # Run all index fetches in parallel
        results = await run_parallel(*[
            lambda ic=ic: _fetch_index_sync(ic) for ic in INDEX_CODES
        ])
        
        indices = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {INDEX_CODES[i]}: {result}")
            elif result:
                indices.append(IndexResponse(**result))
        
        return MarketOverviewResponse(
            indices=indices,
            timestamp=datetime.utcnow(),
        )
    
    async def get_index(self, index_code: str) -> Optional[IndexResponse]:
        """Get single index data."""
        index_code = index_code.upper()
        
        # Try to get from WebSocket cache first
        try:
            from app.infrastructure.streaming.price_stream import price_stream_manager
            cached = price_stream_manager.get_cached_index(index_code)
            if cached:
                return IndexResponse(
                    index_code=index_code,
                    index_value=cached.current_index,
                    change=cached.change,
                    change_percent=cached.percent_change,
                    open_value=cached.open_index,
                    total_volume=cached.volume,
                    total_value=cached.value,
                    advances=cached.advances,
                    declines=cached.declines,
                    unchanged=cached.unchanged,
                    timestamp=datetime.fromtimestamp(cached.timestamp),
                )
        except Exception:
            pass
        
        # Fallback to REST API
        result = await run_sync(_fetch_index_sync, index_code)
        if result:
            return IndexResponse(**result)
        return None
    
    async def get_index_history(
        self, index_code: str, request: IndexHistoryRequest
    ) -> IndexHistoryResponse:
        """Get index historical data."""
        index_code = index_code.upper()
        
        def _fetch():
            try:
                quote = get_quote(index_code)
                df = quote.history(
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                )
                
                if df is None or df.empty:
                    return []
                
                items = []
                for _, row in df.iterrows():
                    items.append({
                        "time": row.get("time"),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": float(row.get("close", 0)),
                        "volume": int(row.get("volume", 0)),
                    })
                return items
            except Exception as e:
                logger.error(f"Error fetching index history {index_code}: {e}")
                return []
        
        items_data = await run_sync(_fetch)
        items = [IndexHistoryItem(**item) for item in items_data]
        
        return IndexHistoryResponse(
            index_code=index_code,
            data=items,
            count=len(items),
        )
            
    async def get_evaluation(self, period: str = 'day', time_window: str = '1D') -> MarketEvaluationResponse:
        """Get market evaluation."""
        def _fetch():
            try:
                import numpy as np
                market = get_market()
                df = market.evaluation(period=period, time_window=time_window, to_df=True)
                if df is None or df.empty:
                    return []
                df = df.replace({np.nan: None})
                return df.to_dict(orient="records")
            except Exception as e:
                logger.error(f"Error fetching market evaluation: {e}")
                return []
        
        data = await run_sync(_fetch)
        
        items = []
        for row in data:
            pe = row.get("pe") if "pe" in row else row.get("PE")
            pb = row.get("pb") if "pb" in row else row.get("PB")
            date_val = row.get("fromDate") if "fromDate" in row else row.get("date")
            
            items.append(MarketEvaluationItem(
                date=str(date_val) if date_val else None,
                pe=self._safe_float(pe),
                pb=self._safe_float(pb),
                vn_type=row.get("vn_type")
            ))
        return MarketEvaluationResponse(data=items, count=len(items))

    @staticmethod
    def _safe_float(val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except:
            return None

    async def get_allocated_value(
        self, 
        group: str = "HOSE", 
        time_frame: str = "ONE_WEEK"
    ) -> AllocatedValueResponse:
        """
        Get allocated value (market breadth / capital flow).
        
        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR
        
        Returns:
            When group=HOSE/HNX/UPCOME: data contains 1 item
            When group=ALL: data contains 3 items (HOSE, HNX, UPCOM)
        """
        from app.application.market.dtos import AllocatedValueItem
        
        provider = VietcapAllocatedValueProvider()
        result = await provider.get_allocated_value(group=group, time_frame=time_frame)
        
        items = []
        
        if result:
            if isinstance(result, list):
                # group=ALL returns list of dicts (one per market)
                for item_data in result:
                    items.append(AllocatedValueItem(
                        total_increase=item_data.get("totalIncrease"),
                        total_nochange=item_data.get("totalNochange"),
                        total_decrease=item_data.get("totalDecrease"),
                        total_symbol_increase=item_data.get("totalSymbolIncrease"),
                        total_symbol_nochange=item_data.get("totalSymbolNochange"),
                        total_symbol_decrease=item_data.get("totalSymbolDecrease")
                    ))
            elif isinstance(result, dict):
                # Single market returns dict
                items.append(AllocatedValueItem(
                    total_increase=result.get("totalIncrease"),
                    total_nochange=result.get("totalNochange"),
                    total_decrease=result.get("totalDecrease"),
                    total_symbol_increase=result.get("totalSymbolIncrease"),
                    total_symbol_nochange=result.get("totalSymbolNochange"),
                    total_symbol_decrease=result.get("totalSymbolDecrease")
                ))
        
        return AllocatedValueResponse(
            data=items,
            group=group.upper(),
            time_frame=time_frame.upper(),
            count=len(items)
        )

    async def get_allocated_icb(
        self, 
        group: str = "HOSE", 
        time_frame: str = "ONE_WEEK"
    ):
        """
        Get allocated ICB (sector allocation by industry).
        
        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR
        
        Returns:
            List of ICB sectors with:
            - icb_code: ICB code
            - icb_change_percent: % change
            - total_price_change: Total price change
            - total_market_cap: Market cap
            - total_value: Trading value
            - total_stock_increase/decrease/no_change: Stock counts
            - icb_code_parent: Parent ICB code
        """
        from app.application.market.dtos import AllocatedICBItem, AllocatedICBResponse
        from app.infrastructure.vietcap.allocated_value_provider import VietcapAllocatedICBProvider
        from app.core.icb_codes import get_icb_mapping
        
        provider = VietcapAllocatedICBProvider()
        result = await provider.get_allocated_icb(group=group, time_frame=time_frame)
        
        # Get ICB mapping for sector names
        icb_mapping = get_icb_mapping()
        
        items = []
        if result and isinstance(result, list):
            for item_data in result:
                icb_code = item_data.get("icb_code")
                
                # Lookup sector names
                sector_info = icb_mapping.get(str(icb_code), {})
                
                items.append(AllocatedICBItem(
                    icb_code=icb_code,
                    sector_name_vi=sector_info.get("vi_sector"),
                    sector_name_en=sector_info.get("en_sector"),
                    icb_level=sector_info.get("level"),
                    icb_change_percent=self._safe_float(item_data.get("icbChangePercent")),
                    total_price_change=self._safe_float(item_data.get("totalPriceChange")),
                    total_market_cap=self._safe_float(item_data.get("totalMarketCap")),
                    total_value=self._safe_float(item_data.get("totalValue")),
                    total_stock_increase=item_data.get("totalStockIncrease"),
                    total_stock_decrease=item_data.get("totalStockDecrease"),
                    total_stock_no_change=item_data.get("totalStockNoChange"),
                    icb_code_parent=item_data.get("icbCodeParent")
                ))
        
        return AllocatedICBResponse(
            data=items,
            group=group.upper(),
            time_frame=time_frame.upper(),
            count=len(items)
        )

    async def get_allocated_icb_detail(
        self, 
        group: str = "HOSE", 
        time_frame: str = "ONE_WEEK",
        icb_code: int = 9500
    ):
        """
        Get allocated ICB detail (stocks within a sector).
        
        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR
            icb_code: ICB code to get stock details for
        
        Returns:
            Sector summary with list of stocks:
            - Sector info (icb_code, change %, market cap, etc.)
            - stocks: List of stocks with symbol, prices, volume, etc.
        """
        from app.application.market.dtos import AllocatedICBStockItem, AllocatedICBDetailResponse
        from app.infrastructure.vietcap.allocated_value_provider import VietcapAllocatedICBProvider
        from app.core.icb_codes import get_icb_mapping
        
        provider = VietcapAllocatedICBProvider()
        
        # Try the exact code first
        result = await provider.get_allocated_icb_detail(
            group=group, 
            time_frame=time_frame,
            icb_code=icb_code
        )
        
        # If no stocks, try alternative codes
        # Vietcap API uses different codes than ICB standard
        # Try sibling codes (e.g., 8301 -> 8300, or vice versa)
        if not result or not result.get("icbDataDetail"):
            # Try rounding to nearest 100 (for level 2 codes)
            alt_code = (icb_code // 100) * 100
            if alt_code != icb_code:
                alt_result = await provider.get_allocated_icb_detail(
                    group=group, 
                    time_frame=time_frame,
                    icb_code=alt_code
                )
                if alt_result and alt_result.get("icbDataDetail"):
                    result = alt_result
                    icb_code = alt_code  # Update for response
        
        if not result:
            # Return empty response
            return AllocatedICBDetailResponse(
                icb_code=icb_code,
                group=group.upper(),
                time_frame=time_frame.upper(),
                stocks=[]
            )
        
        # Get ICB mapping for sector names
        icb_mapping = get_icb_mapping()
        sector_info = icb_mapping.get(str(icb_code), {})
        
        # Parse stocks
        stocks = []
        for stock_data in result.get("icbDataDetail", []):
            ref_price = self._safe_float(stock_data.get("refPrice"))
            match_price = self._safe_float(stock_data.get("matchPrice"))
            
            # Calculate price change if not provided
            price_change = self._safe_float(stock_data.get("priceChange"))
            price_change_percent = self._safe_float(stock_data.get("priceChangePercent"))
            
            if price_change is None and ref_price and match_price:
                price_change = match_price - ref_price
            
            if price_change_percent is None and ref_price and match_price and ref_price > 0:
                price_change_percent = ((match_price - ref_price) / ref_price) * 100
            
            stocks.append(AllocatedICBStockItem(
                symbol=stock_data.get("symbol", ""),
                ref_price=ref_price,
                match_price=match_price,
                ceiling_price=self._safe_float(stock_data.get("ceilingPrice")),
                floor_price=self._safe_float(stock_data.get("floorPrice")),
                accumulated_volume=self._safe_float(stock_data.get("accumulatedVolume")),
                accumulated_value=self._safe_float(stock_data.get("accumulatedValue")),
                price_change=price_change,
                price_change_percent=price_change_percent,
                market_cap=self._safe_float(stock_data.get("marketCap"))
            ))
        
        return AllocatedICBDetailResponse(
            icb_code=result.get("icb_code", icb_code),
            sector_name_vi=sector_info.get("vi_sector"),
            sector_name_en=sector_info.get("en_sector"),
            icb_level=sector_info.get("level"),
            icb_change_percent=self._safe_float(result.get("icbChangePercent")),
            total_price_change=self._safe_float(result.get("totalPriceChange")),
            total_market_cap=self._safe_float(result.get("totalMarketCap")),
            total_value=self._safe_float(result.get("totalValue")),
            total_stock_increase=result.get("totalStockIncrease"),
            total_stock_decrease=result.get("totalStockDecrease"),
            total_stock_no_change=result.get("totalStockNoChange"),
            icb_code_parent=result.get("icbCodeParent"),
            stocks=stocks,
            group=group.upper(),
            time_frame=time_frame.upper()
        )

    async def get_index_impact(
        self, 
        group: str = "ALL", 
        time_frame: str = "ONE_WEEK"
    ):
        """
        Get index impact (market leading stocks).
        
        Args:
            group: Market group - HOSE, HNX, UPCOME, ALL
            time_frame: Time frame - ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR
        
        Returns:
            - top_up: Stocks pulling market up (positive impact)
            - top_down: Stocks pulling market down (negative impact)
        """
        from app.application.market.dtos import IndexImpactStockItem, IndexImpactResponse
        from app.infrastructure.vietcap.allocated_value_provider import VietcapIndexImpactProvider
        
        provider = VietcapIndexImpactProvider()
        result = await provider.get_index_impact(group=group, time_frame=time_frame)
        
        top_up = []
        top_down = []
        
        if result:
            # Parse top up stocks
            for stock_data in result.get("topUp", []):
                top_up.append(IndexImpactStockItem(
                    symbol=stock_data.get("symbol", ""),
                    impact=self._safe_float(stock_data.get("impact")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice")),
                    ceiling=self._safe_float(stock_data.get("ceiling")),
                    floor=self._safe_float(stock_data.get("floor"))
                ))
            
            # Parse top down stocks
            for stock_data in result.get("topDown", []):
                top_down.append(IndexImpactStockItem(
                    symbol=stock_data.get("symbol", ""),
                    impact=self._safe_float(stock_data.get("impact")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice")),
                    ceiling=self._safe_float(stock_data.get("ceiling")),
                    floor=self._safe_float(stock_data.get("floor"))
                ))
        
        return IndexImpactResponse(
            top_up=top_up,
            top_down=top_down,
            group=group.upper(),
            time_frame=time_frame.upper()
        )

    async def get_top_proprietary(
        self, 
        exchange: str = "ALL", 
        time_frame: str = "ONE_WEEK"
    ):
        """Get top proprietary trading (self-trading by brokers)."""
        from app.application.market.dtos import ProprietaryStockItem, TopProprietaryResponse
        from app.infrastructure.vietcap.allocated_value_provider import VietcapTopProprietaryProvider
        
        provider = VietcapTopProprietaryProvider()
        result = await provider.get_top_proprietary(exchange=exchange, time_frame=time_frame)
        
        buy = []
        sell = []
        trading_date = None
        
        if result:
            trading_date = result.get("tradingDate")
            data = result.get("data", {})
            
            # Parse BUY
            for stock_data in data.get("BUY", []):
                buy.append(ProprietaryStockItem(
                    ticker=stock_data.get("ticker", ""),
                    total_value=self._safe_float(stock_data.get("totalValue")),
                    total_volume=self._safe_float(stock_data.get("totalVolume")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice"))
                ))
            
            # Parse SELL
            for stock_data in data.get("SELL", []):
                sell.append(ProprietaryStockItem(
                    ticker=stock_data.get("ticker", ""),
                    total_value=self._safe_float(stock_data.get("totalValue")),
                    total_volume=self._safe_float(stock_data.get("totalVolume")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice"))
                ))
        
        return TopProprietaryResponse(
            trading_date=trading_date,
            buy=buy,
            sell=sell,
            exchange=exchange.upper(),
            time_frame=time_frame.upper()
        )

    async def get_foreign_net_value(
        self, 
        group: str = "ALL", 
        time_frame: str = "ONE_WEEK"
    ):
        """Get foreign net value (foreign investor buy/sell)."""
        from app.application.market.dtos import ForeignNetStockItem, ForeignNetValueResponse
        from app.infrastructure.vietcap.allocated_value_provider import VietcapForeignNetValueProvider
        
        provider = VietcapForeignNetValueProvider()
        result = await provider.get_foreign_net_value(group=group, time_frame=time_frame)
        
        net_buy = []
        net_sell = []
        
        if result:
            # Parse netBuy
            for stock_data in result.get("netBuy", []):
                net_buy.append(ForeignNetStockItem(
                    symbol=stock_data.get("symbol", ""),
                    net=self._safe_float(stock_data.get("net")),
                    foreign_buy_value=self._safe_float(stock_data.get("foreignBuyValue")),
                    foreign_sell_value=self._safe_float(stock_data.get("foreignSellValue")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice"))
                ))
            
            # Parse netSell
            for stock_data in result.get("netSell", []):
                net_sell.append(ForeignNetStockItem(
                    symbol=stock_data.get("symbol", ""),
                    net=self._safe_float(stock_data.get("net")),
                    foreign_buy_value=self._safe_float(stock_data.get("foreignBuyValue")),
                    foreign_sell_value=self._safe_float(stock_data.get("foreignSellValue")),
                    exchange=stock_data.get("exchange"),
                    organ_name=stock_data.get("organName"),
                    organ_short_name=stock_data.get("organShortName"),
                    en_organ_name=stock_data.get("enOrganName"),
                    en_organ_short_name=stock_data.get("enOrganShortName"),
                    match_price=self._safe_float(stock_data.get("matchPrice")),
                    ref_price=self._safe_float(stock_data.get("refPrice"))
                ))
        
        return ForeignNetValueResponse(
            net_buy=net_buy,
            net_sell=net_sell,
            group=group.upper(),
            time_frame=time_frame.upper()
        )

