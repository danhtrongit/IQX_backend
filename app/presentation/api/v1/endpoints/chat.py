"""Chat API endpoints - Mr.Arix AI Assistant."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.application.chat.dtos import ChatRequest, ChatResponse
from app.application.chat.services import ChatService, DataExecutor
from app.presentation.deps.services import (
    get_symbol_service,
    get_quote_service,
    get_financial_service,
    get_company_service,
    get_insight_service,
    get_trading_insight_service,
)
from app.infrastructure.streaming.price_stream import price_stream_manager

router = APIRouter(prefix="/chat", tags=["Chat - Mr.Arix"])

# Global chat service instance
_chat_service: ChatService = None


def get_chat_service(
    symbol_service=Depends(get_symbol_service),
    quote_service=Depends(get_quote_service),
    financial_service=Depends(get_financial_service),
    company_service=Depends(get_company_service),
    insight_service=Depends(get_insight_service),
    trading_insight_service=Depends(get_trading_insight_service),
) -> ChatService:
    """Get or create chat service."""
    global _chat_service
    
    if _chat_service is None:
        data_executor = DataExecutor(
            symbol_service=symbol_service,
            quote_service=quote_service,
            financial_service=financial_service,
            company_service=company_service,
            insight_service=insight_service,
            trading_insight_service=trading_insight_service,
            price_stream_manager=price_stream_manager,
        )
        _chat_service = ChatService(data_executor)
    
    return _chat_service


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Chat với Mr.Arix - Chuyên gia thông tin chứng khoán IQX.

    Mr.Arix có thể trả lời các câu hỏi về:
    - Giá cổ phiếu realtime
    - Thông tin công ty (giới thiệu, cổ đông, ban lãnh đạo)
    - Báo cáo tài chính (bảng cân đối, kết quả kinh doanh, dòng tiền)
    - Chỉ số tài chính (PE, PB, ROE, ROA, EPS...)
    - Tin tức và sự kiện công ty
    - Top cổ phiếu tăng/giảm/khối lượng
    - Giao dịch khối ngoại
    - Chỉ số thị trường (VNINDEX, VN30, HNX, UPCOM)

    **Ví dụ câu hỏi:**
    - "Giá VNM hiện tại bao nhiêu?"
    - "Cho tôi thông tin về công ty Vinamilk"
    - "Cổ đông lớn của FPT là ai?"
    - "PE, PB của VCB là bao nhiêu?"
    - "Top 5 cổ phiếu tăng mạnh nhất hôm nay"
    - "Khối ngoại đang mua ròng những mã nào?"
    - "Báo cáo tài chính quý gần nhất của HPG"

    **Streaming:** Set `stream=true` để nhận response theo realtime (SSE format)

    **Lưu ý:** Mr.Arix chỉ cung cấp thông tin, KHÔNG tư vấn đầu tư.
    """
    # Check if streaming is requested
    if request.stream:
        return StreamingResponse(
            chat_service.chat_stream(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    return await chat_service.chat(request)


@router.get("/info")
async def get_info():
    """Thông tin về Mr.Arix."""
    return {
        "name": "Mr.Arix",
        "role": "Chuyên gia thông tin chứng khoán IQX",
        "capabilities": [
            "Tra cứu giá cổ phiếu realtime",
            "Thông tin công ty (giới thiệu, lịch sử, ngành nghề)",
            "Danh sách cổ đông lớn",
            "Ban lãnh đạo, HĐQT",
            "Báo cáo tài chính (CĐKT, KQKD, LCTT)",
            "Chỉ số tài chính (PE, PB, ROE, ROA, EPS, BVPS)",
            "Tin tức và sự kiện công ty",
            "Top cổ phiếu tăng/giảm/khối lượng/giá trị",
            "Giao dịch khối ngoại",
            "Chỉ số thị trường (VNINDEX, VN30, HNX, UPCOM)",
            "Lịch sử giá cổ phiếu",
        ],
        "disclaimer": "Mr.Arix chỉ cung cấp thông tin, KHÔNG tư vấn đầu tư, KHÔNG khuyến nghị mua/bán.",
        "supported_symbols": "Tất cả mã trên HOSE, HNX, UPCOM",
    }
