"""Chat service with AI integration - Optimized with OpenAI library."""
import json
import uuid
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta

from openai import AsyncOpenAI
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.cache import get_cache, CacheTTL
from app.application.chat.dtos import ChatRequest, ChatResponse, FunctionCall
from app.application.chat.functions import get_function_definitions_openai

logger = get_logger(__name__)

# System prompt for Mr.Arix
SYSTEM_PROMPT = """Bạn là Mr.Arix - chuyên gia thông tin chứng khoán của IQX.

NGUYÊN TẮC:
1. Chỉ cung cấp THÔNG TIN, KHÔNG tư vấn đầu tư, KHÔNG khuyến nghị mua/bán
2. Trả lời bằng tiếng Việt, format markdown đẹp
3. Tự động nhận diện mã cổ phiếu từ câu hỏi (VD: "giá VNM" -> symbol=VNM)
4. Nếu người dùng hỏi về công ty mà không nói rõ mã, hãy tìm kiếm trước
5. KHÔNG BAO GIỜ dùng bảng markdown (không dùng |---|)
6. Trình bày dạng danh sách với bullet points hoặc số thứ tự
7. Luôn ghi nguồn dữ liệu và thời gian cập nhật

CÁCH NHẬN DIỆN SYMBOL:
- Mã 3 chữ cái viết hoa: VNM, FPT, VCB, HPG, MWG, TCB...
- Tên công ty: "Vinamilk" -> VNM, "FPT" -> FPT, "Vietcombank" -> VCB
- Nếu không chắc, dùng search_symbol để tìm

KHI TRẢ LỜI:
- Giá: format x1000 VND (VD: 75.5 = 75,500 VND)
- Khối lượng: format với K/M (VD: 1.5M = 1,500,000)
- Tỷ lệ %: giữ 2 số thập phân
- Tiền: format với tỷ/triệu VND

VÍ DỤ TRẢ LỜI:
```
## 📊 Thông tin cổ phiếu VNM

- **Giá hiện tại:** 75,500 VND
- **Thay đổi:** +1.5%
- **Khối lượng:** 1.2M

*Cập nhật: 14:30 17/12/2025*
```"""


class ChatService:
    """Chat service with AI function calling - Optimized with OpenAI SDK."""

    def __init__(self, data_executor: "DataExecutor"):
        self.data_executor = data_executor
        self._conversations: Dict[str, List[Dict]] = {}

        # Initialize OpenAI client with proxy and custom httpx client for connection pooling
        self._openai_client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client with proxy support and connection pooling."""
        if self._openai_client is None:
            # Create custom httpx client with connection pooling and timeout
            http_client = httpx.AsyncClient(
                base_url=settings.AI_PROXY,
                timeout=httpx.Timeout(settings.AI_TIMEOUT, connect=10.0),
                limits=httpx.Limits(
                    max_keepalive_connections=20,  # Increased from 10
                    max_connections=50,  # Increased from 20
                    keepalive_expiry=60.0,  # Increased from 30
                ),
            )

            self._openai_client = AsyncOpenAI(
                api_key=settings.AI_API_KEY,
                base_url=settings.AI_PROXY,
                http_client=http_client,
                max_retries=settings.AI_MAX_RETRIES,
            )

        return self._openai_client

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request with optimized caching."""
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get or create conversation history from cache first
        cache = get_cache()
        cache_key = f"chat:conversation:{conversation_id}"

        history = await cache.get(cache_key)
        if history is None:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = []
            history = self._conversations[conversation_id]
        else:
            # Update in-memory cache too
            self._conversations[conversation_id] = history

        # Add user message
        history.append({"role": "user", "content": request.message})

        # Call AI with function calling
        data_used = []
        response_text = await self._call_ai(history, data_used)

        # Add assistant response to history
        history.append({"role": "assistant", "content": response_text})

        # Keep only last 20 messages
        if len(history) > 20:
            history = history[-20:]

        # Save to both cache and memory
        self._conversations[conversation_id] = history
        await cache.set(cache_key, history, ttl=1800)  # 30 minutes

        return ChatResponse(
            message=response_text,
            conversation_id=conversation_id,
            data_used=data_used if data_used else None,
        )

    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Process chat request with streaming response."""
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get or create conversation history from cache first
        cache = get_cache()
        cache_key = f"chat:conversation:{conversation_id}"

        history = await cache.get(cache_key)
        if history is None:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = []
            history = self._conversations[conversation_id]
        else:
            self._conversations[conversation_id] = history

        # Add user message
        history.append({"role": "user", "content": request.message})

        # Stream AI response
        data_used = []
        full_response = ""

        async for chunk in self._call_ai_stream(history, data_used):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"

        # Send final metadata
        yield f"data: {json.dumps({'done': True, 'data_used': data_used, 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"

        # Add assistant response to history
        history.append({"role": "assistant", "content": full_response})

        # Keep only last 20 messages
        if len(history) > 20:
            history = history[-20:]

        # Save to both cache and memory
        self._conversations[conversation_id] = history
        await cache.set(cache_key, history, ttl=1800)

    async def _call_ai(
        self,
        history: List[Dict],
        data_used: List[str],
    ) -> str:
        """Call AI proxy API with function calling - Optimized single-pass approach."""
        if not settings.AI_API_KEY:
            return "❌ Chưa cấu hình AI_API_KEY. Vui lòng thêm vào .env"

        try:
            client = self._get_client()

            # Build messages with system prompt
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "content": msg["content"]})

            # Initial call with tools
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                tools=get_function_definitions_openai(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2048,
            )

            message = response.choices[0].message

            # Check for tool calls
            if message.tool_calls:
                # Add assistant message with tool calls to history
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Execute all tool calls in parallel
                function_results = []
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    data_used.append(func_name)
                    fn_result = await self.data_executor.execute(func_name, func_args)
                    function_results.append({
                        "name": func_name,
                        "args": func_args,
                        "result": fn_result
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(fn_result, ensure_ascii=False, default=str)
                    })

                # Get final response with tool results (without tools parameter)
                try:
                    final_response = await client.chat.completions.create(
                        model=settings.AI_MODEL,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2048,
                    )

                    content = final_response.choices[0].message.content
                    if content and content.strip():
                        return content

                except Exception as e:
                    logger.error(f"AI final response error: {e}")

                # Fallback: format raw results if AI fails
                return self._format_raw_results(function_results)

            # No tool calls, return direct response
            return message.content or "Tôi không hiểu câu hỏi. Vui lòng hỏi lại."

        except Exception as e:
            logger.error(f"AI API error: {e}")
            return f"❌ Lỗi kết nối AI: {str(e)}"

    async def _call_ai_stream(
        self,
        history: List[Dict],
        data_used: List[str],
    ) -> AsyncGenerator[str, None]:
        """Call AI with streaming response - Optimized approach."""
        if not settings.AI_API_KEY:
            yield "❌ Chưa cấu hình AI_API_KEY. Vui lòng thêm vào .env"
            return

        try:
            client = self._get_client()

            # Build messages with system prompt
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "content": msg["content"]})

            # Initial call with tools (non-streaming to detect function calls)
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                tools=get_function_definitions_openai(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2048,
            )

            message = response.choices[0].message

            # Check for tool calls
            if message.tool_calls:
                # Add assistant message with tool calls to history
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Execute all tool calls
                function_results = []
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    data_used.append(func_name)
                    fn_result = await self.data_executor.execute(func_name, func_args)
                    function_results.append({
                        "name": func_name,
                        "args": func_args,
                        "result": fn_result
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(fn_result, ensure_ascii=False, default=str)
                    })

                # Get final response with streaming
                try:
                    stream = await client.chat.completions.create(
                        model=settings.AI_MODEL,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2048,
                        stream=True,
                    )

                    async for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                except Exception as e:
                    logger.error(f"AI streaming error: {e}")
                    # Fallback: format raw results
                    yield self._format_raw_results(function_results)

            else:
                # No tool calls, stream direct response
                stream = await client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"AI streaming error: {e}")
            yield f"❌ Lỗi kết nối AI: {str(e)}"

    def _format_raw_results(self, results: List[Dict]) -> str:
        """Format raw function results as markdown (no tables)."""
        output = "## 📊 Kết quả tra cứu\n\n"
        for r in results:
            name = r.get("name", "unknown")
            data = r.get("result", {})

            # Format based on function type
            if name == "get_shareholders" and "data" in data:
                output += "### 👥 Danh sách cổ đông\n\n"
                shareholders = data.get("data", [])
                if shareholders:
                    for i, sh in enumerate(shareholders[:10], 1):
                        name_sh = sh.get("share_holder", "N/A")
                        qty = sh.get("share_own", 0)
                        ratio = sh.get("share_own_percent", 0)
                        output += f"{i}. **{name_sh}**\n"
                        output += f"   - Số lượng: {qty:,.0f} CP\n"
                        output += f"   - Tỷ lệ: {ratio:.2f}%\n\n"
                else:
                    output += "Không có dữ liệu cổ đông.\n\n"
            elif name == "get_officers" and "data" in data:
                output += "### 👔 Ban lãnh đạo\n\n"
                officers = data.get("data", [])
                if officers:
                    for i, off in enumerate(officers[:10], 1):
                        full_name = off.get("full_name", "N/A")
                        position = off.get("position", "N/A")
                        output += f"{i}. **{full_name}** - {position}\n"
                else:
                    output += "Không có dữ liệu ban lãnh đạo.\n"
                output += "\n"
            elif name == "get_stock_price":
                if "error" not in data:
                    output += f"### 💰 Giá cổ phiếu {data.get('symbol', '')}\n\n"
                    output += f"- **Giá:** {data.get('price', 0):,.0f} VND\n"
                    output += f"- **Thay đổi:** {data.get('change', 0):+,.0f} ({data.get('change_percent', 0):+.2f}%)\n"
                    output += f"- **Khối lượng:** {data.get('volume', 0):,.0f}\n"
                    output += f"- **Cao nhất:** {data.get('high', 0):,.0f} VND\n"
                    output += f"- **Thấp nhất:** {data.get('low', 0):,.0f} VND\n\n"
                else:
                    output += f"❌ {data['error']}\n\n"
            elif "error" in data:
                output += f"❌ Lỗi: {data['error']}\n\n"
            else:
                output += f"### {name}\n"
                output += f"```json\n{json.dumps(data, indent=2, ensure_ascii=False, default=str)}\n```\n\n"

        output += f"*Cập nhật: {datetime.now().strftime('%H:%M %d/%m/%Y')}*"
        return output


class DataExecutor:
    """Execute data functions."""

    def __init__(
        self,
        symbol_service,
        quote_service,
        financial_service,
        company_service,
        insight_service,
        trading_insight_service,
        price_stream_manager,
    ):
        self.symbol_service = symbol_service
        self.quote_service = quote_service
        self.financial_service = financial_service
        self.company_service = company_service
        self.insight_service = insight_service
        self.trading_insight_service = trading_insight_service
        self.price_stream_manager = price_stream_manager

    async def execute(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a function by name."""
        try:
            if name == "get_stock_price":
                return await self._get_stock_price(args.get("symbol", ""))
            elif name == "get_stock_detail":
                return await self._get_stock_detail(args.get("symbol", ""))
            elif name == "get_company_overview":
                return await self._get_company_overview(args.get("symbol", ""))
            elif name == "get_shareholders":
                return await self._get_shareholders(args.get("symbol", ""))
            elif name == "get_officers":
                return await self._get_officers(args.get("symbol", ""))
            elif name == "get_company_news":
                return await self._get_company_news(args.get("symbol", ""))
            elif name == "get_company_events":
                return await self._get_company_events(args.get("symbol", ""))
            elif name == "get_financial_ratio":
                return await self._get_financial_ratio(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_balance_sheet":
                return await self._get_balance_sheet(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_income_statement":
                return await self._get_income_statement(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_cash_flow":
                return await self._get_cash_flow(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_price_history":
                return await self._get_price_history(
                    args.get("symbol", ""),
                    args.get("days", 30)
                )
            elif name == "get_market_indices":
                return await self._get_market_indices()
            elif name == "get_top_stocks":
                return await self._get_top_stocks(
                    args.get("type", "gainer"),
                    args.get("limit", 10)
                )
            elif name == "get_foreign_trading":
                return await self._get_foreign_trading(
                    args.get("symbol"),
                    args.get("type", "buy")
                )
            elif name == "search_symbol":
                return await self._search_symbol(args.get("query", ""))
            else:
                return {"error": f"Unknown function: {name}"}
        except Exception as e:
            logger.error(f"Function {name} error: {e}")
            return {"error": str(e)}

    async def _get_stock_price(self, symbol: str) -> Dict:
        """Get realtime or latest stock price."""
        symbol = symbol.upper().strip()

        # Try realtime first
        cached = self.price_stream_manager.get_cached_price(symbol)
        if cached:
            return {
                "symbol": symbol,
                "price": cached.last_price,
                "change": cached.change,
                "change_percent": cached.change_percent,
                "volume": cached.total_volume,
                "high": cached.high_price,
                "low": cached.low_price,
                "open": cached.open_price,
                "source": "realtime",
                "timestamp": datetime.now().isoformat()
            }

        # Fallback to history (get latest day)
        try:
            from app.application.quote.dtos import HistoryRequest
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            result = self.quote_service.get_history(
                symbol, HistoryRequest(start=start, interval="1D")
            )
            if result.data:
                latest = result.data[-1]  # Last record is most recent
                ref_price = result.data[-2].close if len(result.data) > 1 else latest.open
                change = latest.close - ref_price
                change_pct = (change / ref_price * 100) if ref_price else 0
                return {
                    "symbol": symbol,
                    "price": latest.close,
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                    "volume": latest.volume,
                    "high": latest.high,
                    "low": latest.low,
                    "open": latest.open,
                    "source": "history",
                    "date": str(latest.time) if hasattr(latest, 'time') else None,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")

        return {"error": f"Không tìm thấy dữ liệu giá cho {symbol}"}

    async def _get_stock_detail(self, symbol: str) -> Dict:
        """Get stock detail (cached)."""
        cache = get_cache()
        cache_key = f"chat:stock_detail:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_stock_detail(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.COMPANY_INFO)
        return data

    async def _get_company_overview(self, symbol: str) -> Dict:
        """Get company overview (cached)."""
        cache = get_cache()
        cache_key = f"chat:company_overview:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_overview(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.COMPANY_OVERVIEW)
        return data

    async def _get_shareholders(self, symbol: str) -> Dict:
        """Get shareholders (cached)."""
        cache = get_cache()
        cache_key = f"chat:shareholders:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_shareholders(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.OFFICERS)
        return data

    async def _get_officers(self, symbol: str) -> Dict:
        """Get officers (cached)."""
        cache = get_cache()
        cache_key = f"chat:officers:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_officers(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.OFFICERS)
        return data

    async def _get_company_news(self, symbol: str) -> Dict:
        """Get company news (cached with shorter TTL)."""
        cache = get_cache()
        cache_key = f"chat:company_news:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_news(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.INTRADAY)
        return data

    async def _get_company_events(self, symbol: str) -> Dict:
        """Get company events (cached with shorter TTL)."""
        cache = get_cache()
        cache_key = f"chat:company_events:{symbol.upper()}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = self.company_service.get_events(symbol)
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.INTRADAY)
        return data

    async def _get_financial_ratio(self, symbol: str, period: str) -> Dict:
        """Get financial ratios (cached)."""
        cache = get_cache()
        cache_key = f"chat:financial_ratio:{symbol.upper()}:{period}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        from app.application.financial.dtos import RatioRequest
        result = self.financial_service.get_ratio(symbol, RatioRequest(period=period, limit=4))
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.FINANCIALS)
        return data

    async def _get_balance_sheet(self, symbol: str, period: str) -> Dict:
        """Get balance sheet (cached)."""
        cache = get_cache()
        cache_key = f"chat:balance_sheet:{symbol.upper()}:{period}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_balance_sheet(
            symbol, FinancialRequest(period=period, limit=4)
        )
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.FINANCIALS)
        return data

    async def _get_income_statement(self, symbol: str, period: str) -> Dict:
        """Get income statement (cached)."""
        cache = get_cache()
        cache_key = f"chat:income_statement:{symbol.upper()}:{period}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_income_statement(
            symbol, FinancialRequest(period=period, limit=4)
        )
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.FINANCIALS)
        return data

    async def _get_cash_flow(self, symbol: str, period: str) -> Dict:
        """Get cash flow (cached)."""
        cache = get_cache()
        cache_key = f"chat:cash_flow:{symbol.upper()}:{period}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_cash_flow(
            symbol, FinancialRequest(period=period, limit=4)
        )
        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.FINANCIALS)
        return data

    async def _get_price_history(self, symbol: str, days: int) -> Dict:
        """Get price history (cached with TTL based on recency)."""
        cache = get_cache()
        cache_key = f"chat:price_history:{symbol.upper()}:{days}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        from app.application.quote.dtos import HistoryRequest
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        result = self.quote_service.get_history(
            symbol, HistoryRequest(start=start, interval="1D")
        )
        data = result.model_dump()

        # Use shorter TTL for recent history
        ttl = CacheTTL.HISTORICAL_RECENT if days <= 30 else CacheTTL.HISTORICAL_OLD
        await cache.set(cache_key, data, ttl)
        return data

    async def _get_market_indices(self) -> Dict:
        """Get market indices from realtime stream (cached with short TTL)."""
        cache = get_cache()
        cache_key = "chat:market_indices"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        indices = self.price_stream_manager.get_all_cached_indices()
        if indices:
            data = {
                "indices": indices,
                "source": "realtime",
                "timestamp": datetime.now().isoformat()
            }
            await cache.set(cache_key, data, CacheTTL.MARKET_OVERVIEW)
            return data
        return {"error": "Chưa có dữ liệu chỉ số. Vui lòng kết nối stream."}

    async def _get_top_stocks(self, type_: str, limit: int) -> Dict:
        """Get top stocks (cached with medium TTL)."""
        cache = get_cache()
        cache_key = f"chat:top_stocks:{type_}:{limit}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        if type_ == "gainer":
            result = self.insight_service.get_top_gainer(limit=limit)
        elif type_ == "loser":
            result = self.insight_service.get_top_loser(limit=limit)
        elif type_ == "volume":
            result = self.insight_service.get_top_volume(limit=limit)
        elif type_ == "value":
            result = self.insight_service.get_top_value(limit=limit)
        else:
            return {"error": f"Unknown type: {type_}"}

        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.TOP_STOCKS)
        return data

    async def _get_foreign_trading(self, symbol: Optional[str], type_: str) -> Dict:
        """Get foreign trading (cached with medium TTL)."""
        cache = get_cache()
        cache_key = f"chat:foreign_trading:{symbol or 'all'}:{type_}"

        cached = await cache.get(cache_key)
        if cached:
            return cached

        if symbol:
            result = self.trading_insight_service.get_foreign_trading(symbol)
        else:
            if type_ == "buy":
                result = self.insight_service.get_top_foreign_buy()
            else:
                result = self.insight_service.get_top_foreign_sell()

        data = result.model_dump()
        await cache.set(cache_key, data, CacheTTL.INTRADAY)
        return data

    async def _search_symbol(self, query: str) -> Dict:
        """Search symbol."""
        from app.application.symbol.dtos import SymbolSearchRequest
        results = await self.symbol_service.search_symbols(
            SymbolSearchRequest(query=query, limit=5)
        )
        return {
            "results": [r.model_dump() for r in results],
            "count": len(results)
        }
