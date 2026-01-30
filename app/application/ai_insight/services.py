"""AI Insight service for technical analysis using Gemini."""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import httpx

from app.core.logging import get_logger
from app.application.ai_insight.dtos import (
    AIInsightRequest,
    AIInsightResponse,
    TradingRecommendation,
    OHLCDataPoint,
)

logger = get_logger(__name__)


# System prompt for technical analysis
SYSTEM_PROMPT = """Bạn là trợ lý phân tích kỹ thuật. Dữ liệu đầu vào gồm OHLCV 200 ngày, MA10/20/30/100/200, khối lượng trung bình 10/20/30/100/200 phiên, và mẫu hình nến hiện tại.

Hãy trả lời đúng 4 mục:
1. Mô tả: Phân tích xu hướng hiện tại, vị trí giá so với các đường MA, và nhận định ngắn hạn
2. Giá mua + điều kiện mua: Dùng khối lượng trung bình và MA để xác định điều kiện mua
3. Giá cắt lỗ + điều kiện cắt lỗ: Xác định mức cắt lỗ dựa trên các mức hỗ trợ và MA
4. Giá chốt lời + điều kiện chốt lời: Xác định mức chốt lời dựa trên các mức kháng cự và MA

Quy tắc:
- Viết rõ ràng, ít thuật ngữ, điều kiện phải đo được
- Ví dụ điều kiện: đóng cửa vượt X, volume ≥ 1.2× trung bình 20 phiên, giữ trên MA20
- Giá phải format theo đơn vị VNĐ (x1000)
- Trả lời bằng tiếng Việt

Trả về JSON với cấu trúc:
{
    "description": "Mô tả phân tích chi tiết",
    "buy_price": "Giá mua đề xuất (VNĐ)",
    "buy_conditions": ["Điều kiện 1", "Điều kiện 2"],
    "stop_loss_price": "Giá cắt lỗ (VNĐ)",
    "stop_loss_conditions": ["Điều kiện 1", "Điều kiện 2"],
    "take_profit_price": "Giá chốt lời (VNĐ)",
    "take_profit_conditions": ["Điều kiện 1", "Điều kiện 2"]
}"""


class CandlestickPatternDetector:
    """Detect candlestick patterns from OHLC data."""

    @staticmethod
    def detect_pattern(data: List[OHLCDataPoint]) -> str:
        """Detect the current candlestick pattern."""
        if len(data) < 3:
            return "Không đủ dữ liệu"

        # Get last 3 candles
        current = data[-1]
        prev = data[-2]
        prev2 = data[-3]

        patterns = []

        # Calculate body and shadows
        body = current.close - current.open
        body_size = abs(body)
        upper_shadow = current.high - max(current.open, current.close)
        lower_shadow = min(current.open, current.close) - current.low
        total_range = current.high - current.low

        if total_range == 0:
            return "Doji (nến không có biên độ)"

        body_ratio = body_size / total_range

        # Doji pattern
        if body_ratio < 0.1:
            patterns.append("Doji")

        # Hammer / Hanging Man
        if (lower_shadow > 2 * body_size and upper_shadow < body_size * 0.3):
            if body > 0:
                patterns.append("Hammer (Búa - tín hiệu tăng)")
            else:
                patterns.append("Hanging Man (Người treo - tín hiệu đảo chiều)")

        # Inverted Hammer / Shooting Star
        if (upper_shadow > 2 * body_size and lower_shadow < body_size * 0.3):
            if body > 0:
                patterns.append("Inverted Hammer (Búa ngược)")
            else:
                patterns.append("Shooting Star (Sao băng - tín hiệu giảm)")

        # Marubozu (strong candle with minimal shadows)
        if body_ratio > 0.9:
            if body > 0:
                patterns.append("Bullish Marubozu (Nến tăng mạnh)")
            else:
                patterns.append("Bearish Marubozu (Nến giảm mạnh)")

        # Engulfing patterns
        prev_body = prev.close - prev.open
        if (prev_body < 0 and body > 0 and
            current.open < prev.close and current.close > prev.open):
            patterns.append("Bullish Engulfing (Nhấn chìm tăng)")
        elif (prev_body > 0 and body < 0 and
              current.open > prev.close and current.close < prev.open):
            patterns.append("Bearish Engulfing (Nhấn chìm giảm)")

        # Morning Star / Evening Star (3-candle pattern)
        prev2_body = prev2.close - prev2.open
        if (prev2_body < 0 and abs(prev.close - prev.open) / prev.close < 0.01 and body > 0):
            patterns.append("Morning Star (Sao mai - tín hiệu tăng)")
        elif (prev2_body > 0 and abs(prev.close - prev.open) / prev.close < 0.01 and body < 0):
            patterns.append("Evening Star (Sao hôm - tín hiệu giảm)")

        if not patterns:
            if body > 0:
                patterns.append("Nến tăng thông thường")
            else:
                patterns.append("Nến giảm thông thường")

        return ", ".join(patterns)


class AIInsightService:
    """Service for AI-powered technical analysis using Gemini."""

    def __init__(
        self,
        proxy_url: str,
        api_key: str,
        model: str = "claude-opus-4-5-thinking",
    ):
        self.proxy_url = proxy_url.rstrip("/")
        if not self.proxy_url.endswith("/chat/completions"):
            self.proxy_url = f"{self.proxy_url}/chat/completions"

        self.api_key = api_key
        self.model = model
        self.pattern_detector = CandlestickPatternDetector()

    async def get_insight(
        self,
        symbol: str,
        ohlc_data: List[OHLCDataPoint],
        request: AIInsightRequest,
    ) -> AIInsightResponse:
        """Get AI insight for a stock symbol."""
        try:
            if not ohlc_data:
                return AIInsightResponse(
                    symbol=symbol,
                    period=request.period,
                    error="Không có dữ liệu OHLC cho mã này"
                )

            # Limit data to requested period
            period_data = ohlc_data[-request.period:] if len(ohlc_data) > request.period else ohlc_data

            # Get current price and volume
            current = ohlc_data[-1]
            current_price = current.close
            current_volume = current.volume

            # Detect candlestick pattern
            pattern = self.pattern_detector.detect_pattern(ohlc_data)

            # Build context for AI
            context = self._build_context(symbol, ohlc_data, period_data, pattern)

            # Call Gemini API
            analysis = await self._call_gemini(context)

            if analysis is None:
                return AIInsightResponse(
                    symbol=symbol,
                    period=request.period,
                    current_price=current_price,
                    current_volume=current_volume,
                    candlestick_pattern=pattern,
                    error="Không thể lấy phân tích từ AI"
                )

            # Parse AI response
            recommendation = self._parse_response(analysis)

            return AIInsightResponse(
                symbol=symbol,
                period=request.period,
                current_price=current_price,
                current_volume=current_volume,
                recommendation=recommendation,
                raw_analysis=analysis,
                candlestick_pattern=pattern,
            )

        except Exception as e:
            logger.error(f"Error getting AI insight for {symbol}: {e}")
            return AIInsightResponse(
                symbol=symbol,
                period=request.period,
                error=str(e)
            )

    def _build_context(
        self,
        symbol: str,
        full_data: List[OHLCDataPoint],
        period_data: List[OHLCDataPoint],
        pattern: str,
    ) -> str:
        """Build context string for AI analysis."""
        current = full_data[-1]

        # Calculate key statistics
        latest_close = current.close
        latest_volume = current.volume

        # MA values from latest data point
        ma_info = []
        if current.ma10:
            pct = ((latest_close - current.ma10) / current.ma10 * 100)
            ma_info.append(f"MA10: {current.ma10:,.0f} ({pct:+.2f}%)")
        if current.ma20:
            pct = ((latest_close - current.ma20) / current.ma20 * 100)
            ma_info.append(f"MA20: {current.ma20:,.0f} ({pct:+.2f}%)")
        if current.ma30:
            pct = ((latest_close - current.ma30) / current.ma30 * 100)
            ma_info.append(f"MA30: {current.ma30:,.0f} ({pct:+.2f}%)")
        if current.ma100:
            pct = ((latest_close - current.ma100) / current.ma100 * 100)
            ma_info.append(f"MA100: {current.ma100:,.0f} ({pct:+.2f}%)")
        if current.ma200:
            pct = ((latest_close - current.ma200) / current.ma200 * 100)
            ma_info.append(f"MA200: {current.ma200:,.0f} ({pct:+.2f}%)")

        # Volume MA values
        vol_info = []
        if current.vol_ma10:
            ratio = latest_volume / current.vol_ma10
            vol_info.append(f"TB 10 phiên: {current.vol_ma10:,} (hiện tại: {ratio:.2f}x)")
        if current.vol_ma20:
            ratio = latest_volume / current.vol_ma20
            vol_info.append(f"TB 20 phiên: {current.vol_ma20:,} (hiện tại: {ratio:.2f}x)")
        if current.vol_ma30:
            ratio = latest_volume / current.vol_ma30
            vol_info.append(f"TB 30 phiên: {current.vol_ma30:,} (hiện tại: {ratio:.2f}x)")
        if current.vol_ma100:
            ratio = latest_volume / current.vol_ma100
            vol_info.append(f"TB 100 phiên: {current.vol_ma100:,} (hiện tại: {ratio:.2f}x)")
        if current.vol_ma200:
            ratio = latest_volume / current.vol_ma200
            vol_info.append(f"TB 200 phiên: {current.vol_ma200:,} (hiện tại: {ratio:.2f}x)")

        # Recent price action
        if len(full_data) >= 5:
            price_5d = full_data[-5].close
            change_5d = ((latest_close - price_5d) / price_5d * 100)
        else:
            change_5d = 0

        if len(full_data) >= 20:
            price_20d = full_data[-20].close
            change_20d = ((latest_close - price_20d) / price_20d * 100)
        else:
            change_20d = 0

        # Find support/resistance from period data
        highs = [d.high for d in period_data]
        lows = [d.low for d in period_data]
        resistance = max(highs)
        support = min(lows)

        # OHLCV summary for period
        ohlcv_summary = []
        for i, d in enumerate(period_data[-10:]):  # Last 10 days only for context
            ohlcv_summary.append(
                f"{d.trade_date}: O={d.open:,.0f} H={d.high:,.0f} L={d.low:,.0f} C={d.close:,.0f} V={d.volume:,}"
            )

        context = f"""
## Phân tích kỹ thuật mã {symbol}

### Giá hiện tại
- Giá đóng cửa: {latest_close:,.0f} VNĐ
- Khối lượng: {latest_volume:,}
- Mẫu hình nến: {pattern}

### Biến động giá
- 5 phiên gần nhất: {change_5d:+.2f}%
- 20 phiên gần nhất: {change_20d:+.2f}%

### Vùng hỗ trợ/kháng cự ({len(period_data)} phiên)
- Kháng cự: {resistance:,.0f}
- Hỗ trợ: {support:,.0f}

### Đường trung bình giá (MA)
{chr(10).join(ma_info) if ma_info else "Không có dữ liệu MA"}

### Khối lượng trung bình
{chr(10).join(vol_info) if vol_info else "Không có dữ liệu khối lượng TB"}

### OHLCV 10 phiên gần nhất
{chr(10).join(ohlcv_summary)}
"""
        return context

    async def _call_gemini(self, context: str) -> Optional[str]:
        """Call Gemini API via proxy."""
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ]

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.proxy_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2048,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

    def _parse_response(self, response: str) -> Optional[TradingRecommendation]:
        """Parse AI response into TradingRecommendation."""
        try:
            # Try to extract JSON from response
            # Handle case where response might have markdown code blocks
            json_str = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()

            # Try to find JSON object in the response
            if "{" in json_str:
                start = json_str.find("{")
                end = json_str.rfind("}") + 1
                json_str = json_str[start:end]

            data = json.loads(json_str)

            return TradingRecommendation(
                description=data.get("description", ""),
                buy_price=data.get("buy_price"),
                buy_conditions=data.get("buy_conditions", []),
                stop_loss_price=data.get("stop_loss_price"),
                stop_loss_conditions=data.get("stop_loss_conditions", []),
                take_profit_price=data.get("take_profit_price"),
                take_profit_conditions=data.get("take_profit_conditions", []),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            # Return raw response as description
            return TradingRecommendation(
                description=response,
                buy_conditions=[],
                stop_loss_conditions=[],
                take_profit_conditions=[],
            )
