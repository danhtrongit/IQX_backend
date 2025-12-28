"""Available functions for AI to call."""
from typing import Dict, Any, List

# Function definitions for AI
AVAILABLE_FUNCTIONS = [
    {
        "name": "get_stock_price",
        "description": "Lấy giá cổ phiếu realtime hoặc giá đóng cửa gần nhất của một mã chứng khoán",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu (VD: VNM, FPT, VCB)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_stock_detail",
        "description": "Lấy thông tin chi tiết cổ phiếu: giá, vốn hóa, PE, PB, EPS, ROE, ROA, tỷ lệ sở hữu nước ngoài",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_company_overview",
        "description": "Lấy thông tin tổng quan công ty: giới thiệu, lịch sử, ngành nghề",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_shareholders",
        "description": "Lấy danh sách cổ đông lớn của công ty",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_officers",
        "description": "Lấy danh sách ban lãnh đạo, hội đồng quản trị của công ty",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_company_news",
        "description": "Lấy tin tức mới nhất về công ty",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_company_events",
        "description": "Lấy các sự kiện công ty: cổ tức, chia tách, phát hành",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_financial_ratio",
        "description": "Lấy các chỉ số tài chính: ROE, ROA, EPS, PE, PB, biên lợi nhuận",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                },
                "period": {
                    "type": "string",
                    "description": "Kỳ báo cáo: quarter (quý) hoặc year (năm)",
                    "enum": ["quarter", "year"]
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_balance_sheet",
        "description": "Lấy bảng cân đối kế toán: tài sản, nợ phải trả, vốn chủ sở hữu",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                },
                "period": {
                    "type": "string",
                    "description": "Kỳ báo cáo: quarter hoặc year",
                    "enum": ["quarter", "year"]
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_income_statement",
        "description": "Lấy báo cáo kết quả kinh doanh: doanh thu, lợi nhuận",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                },
                "period": {
                    "type": "string",
                    "description": "Kỳ báo cáo: quarter hoặc year",
                    "enum": ["quarter", "year"]
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_cash_flow",
        "description": "Lấy báo cáo lưu chuyển tiền tệ",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                },
                "period": {
                    "type": "string",
                    "description": "Kỳ báo cáo: quarter hoặc year",
                    "enum": ["quarter", "year"]
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_price_history",
        "description": "Lấy lịch sử giá cổ phiếu (OHLCV)",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu"
                },
                "days": {
                    "type": "integer",
                    "description": "Số ngày lịch sử (mặc định 30)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_market_indices",
        "description": "Lấy thông tin các chỉ số thị trường: VNINDEX, VN30, HNX, UPCOM",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_top_stocks",
        "description": "Lấy top cổ phiếu theo tiêu chí: tăng giá, giảm giá, khối lượng, giá trị giao dịch",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Loại top: gainer (tăng), loser (giảm), volume (khối lượng), value (giá trị)",
                    "enum": ["gainer", "loser", "volume", "value"]
                },
                "limit": {
                    "type": "integer",
                    "description": "Số lượng kết quả (mặc định 10)"
                }
            },
            "required": ["type"]
        }
    },
    {
        "name": "get_foreign_trading",
        "description": "Lấy thông tin giao dịch khối ngoại của một mã hoặc top mua/bán ròng",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu (để trống để lấy top)"
                },
                "type": {
                    "type": "string",
                    "description": "Loại: buy (mua ròng), sell (bán ròng)",
                    "enum": ["buy", "sell"]
                }
            }
        }
    },
    {
        "name": "search_symbol",
        "description": "Tìm kiếm mã cổ phiếu theo tên công ty hoặc mã",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa tìm kiếm (tên công ty hoặc mã)"
                }
            },
            "required": ["query"]
        }
    }
]


def get_function_definitions_openai() -> List[Dict[str, Any]]:
    """Get function definitions for OpenAI format."""
    return [
        {
            "type": "function",
            "function": {
                "name": f["name"],
                "description": f["description"],
                "parameters": f["parameters"]
            }
        }
        for f in AVAILABLE_FUNCTIONS
    ]
