"""Chat service with AI integration."""
import json
import uuid
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging import get_logger
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
    """Chat service with AI function calling."""

    def __init__(self, data_executor: "DataExecutor"):
        self.data_executor = data_executor
        self._conversations: Dict[str, List[Dict]] = {}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request."""
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        
        history = self._conversations[conversation_id]
        
        # Add user message
        history.append({"role": "user", "content": request.message})
        
        # Call AI with function calling
        data_used = []
        response_text = await self._call_ai(history, data_used)
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": response_text})
        
        # Keep only last 20 messages
        if len(history) > 20:
            self._conversations[conversation_id] = history[-20:]
        
        return ChatResponse(
            message=response_text,
            conversation_id=conversation_id,
            data_used=data_used if data_used else None,
        )

    async def _call_ai(
        self,
        history: List[Dict],
        data_used: List[str],
    ) -> str:
        """Call AI proxy API with function calling."""
        if not settings.AI_API_KEY:
            return "❌ Chưa cấu hình AI_API_KEY. Vui lòng thêm vào .env"

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "tools": get_function_definitions_openai(),
            "tool_choice": "auto",
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.AI_API_KEY}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(settings.AI_PROXY, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    logger.error(f"AI proxy error: {error}")
                    return f"❌ Lỗi kết nối AI: {resp.status}"
                
                result = await resp.json()

            choice = result.get("choices", [{}])[0]
            msg = choice.get("message", {})
            
            # Check for tool calls
            tool_calls = msg.get("tool_calls", [])
            
            if tool_calls:
                # Execute functions and store results
                messages.append(msg)
                function_results = []
                
                for tc in tool_calls:
                    func = tc.get("function", {})
                    name = func.get("name", "")
                    args = json.loads(func.get("arguments", "{}"))
                    
                    data_used.append(name)
                    fn_result = await self.data_executor.execute(name, args)
                    function_results.append({"name": name, "args": args, "result": fn_result})
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(fn_result, ensure_ascii=False, default=str)
                    })

                # Get final response (without tools)
                payload["messages"] = messages
                del payload["tools"]
                del payload["tool_choice"]

                try:
                    async with session.post(settings.AI_PROXY, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if content and content.strip():
                                return content
                except Exception as e:
                    logger.error(f"AI final response error: {e}")
                
                # Fallback: format raw results if AI fails or returns empty
                return self._format_raw_results(function_results)

            return msg.get("content") or "Tôi không hiểu câu hỏi. Vui lòng hỏi lại."

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
                return self._get_stock_detail(args.get("symbol", ""))
            elif name == "get_company_overview":
                return self._get_company_overview(args.get("symbol", ""))
            elif name == "get_shareholders":
                return self._get_shareholders(args.get("symbol", ""))
            elif name == "get_officers":
                return self._get_officers(args.get("symbol", ""))
            elif name == "get_company_news":
                return self._get_company_news(args.get("symbol", ""))
            elif name == "get_company_events":
                return self._get_company_events(args.get("symbol", ""))
            elif name == "get_financial_ratio":
                return self._get_financial_ratio(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_balance_sheet":
                return self._get_balance_sheet(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_income_statement":
                return self._get_income_statement(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_cash_flow":
                return self._get_cash_flow(
                    args.get("symbol", ""),
                    args.get("period", "quarter")
                )
            elif name == "get_price_history":
                return self._get_price_history(
                    args.get("symbol", ""),
                    args.get("days", 30)
                )
            elif name == "get_market_indices":
                return self._get_market_indices()
            elif name == "get_top_stocks":
                return self._get_top_stocks(
                    args.get("type", "gainer"),
                    args.get("limit", 10)
                )
            elif name == "get_foreign_trading":
                return self._get_foreign_trading(
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

    def _get_stock_detail(self, symbol: str) -> Dict:
        """Get stock detail."""
        result = self.company_service.get_stock_detail(symbol)
        return result.model_dump()

    def _get_company_overview(self, symbol: str) -> Dict:
        """Get company overview."""
        result = self.company_service.get_overview(symbol)
        return result.model_dump()

    def _get_shareholders(self, symbol: str) -> Dict:
        """Get shareholders."""
        result = self.company_service.get_shareholders(symbol)
        return result.model_dump()

    def _get_officers(self, symbol: str) -> Dict:
        """Get officers."""
        result = self.company_service.get_officers(symbol)
        return result.model_dump()

    def _get_company_news(self, symbol: str) -> Dict:
        """Get company news."""
        result = self.company_service.get_news(symbol)
        return result.model_dump()

    def _get_company_events(self, symbol: str) -> Dict:
        """Get company events."""
        result = self.company_service.get_events(symbol)
        return result.model_dump()

    def _get_financial_ratio(self, symbol: str, period: str) -> Dict:
        """Get financial ratios."""
        from app.application.financial.dtos import RatioRequest
        result = self.financial_service.get_ratio(symbol, RatioRequest(period=period, limit=4))
        return result.model_dump()

    def _get_balance_sheet(self, symbol: str, period: str) -> Dict:
        """Get balance sheet."""
        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_balance_sheet(
            symbol, FinancialRequest(period=period, limit=4)
        )
        return result.model_dump()

    def _get_income_statement(self, symbol: str, period: str) -> Dict:
        """Get income statement."""
        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_income_statement(
            symbol, FinancialRequest(period=period, limit=4)
        )
        return result.model_dump()

    def _get_cash_flow(self, symbol: str, period: str) -> Dict:
        """Get cash flow."""
        from app.application.financial.dtos import FinancialRequest
        result = self.financial_service.get_cash_flow(
            symbol, FinancialRequest(period=period, limit=4)
        )
        return result.model_dump()

    def _get_price_history(self, symbol: str, days: int) -> Dict:
        """Get price history."""
        from app.application.quote.dtos import HistoryRequest
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        result = self.quote_service.get_history(
            symbol, HistoryRequest(start=start, interval="1D")
        )
        return result.model_dump()

    def _get_market_indices(self) -> Dict:
        """Get market indices from realtime stream."""
        indices = self.price_stream_manager.get_all_cached_indices()
        if indices:
            return {
                "indices": indices,
                "source": "realtime",
                "timestamp": datetime.now().isoformat()
            }
        return {"error": "Chưa có dữ liệu chỉ số. Vui lòng kết nối stream."}

    def _get_top_stocks(self, type_: str, limit: int) -> Dict:
        """Get top stocks."""
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
        return result.model_dump()

    def _get_foreign_trading(self, symbol: Optional[str], type_: str) -> Dict:
        """Get foreign trading."""
        if symbol:
            result = self.trading_insight_service.get_foreign_trading(symbol)
            return result.model_dump()
        else:
            if type_ == "buy":
                result = self.insight_service.get_top_foreign_buy()
            else:
                result = self.insight_service.get_top_foreign_sell()
            return result.model_dump()

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
