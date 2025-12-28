"""Chat DTOs."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request."""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Chat response."""
    message: str = Field(..., description="Assistant response in markdown")
    conversation_id: str = Field(..., description="Conversation ID")
    data_used: Optional[List[str]] = Field(None, description="List of data sources used")


class FunctionCall(BaseModel):
    """Function call from AI."""
    name: str
    arguments: Dict[str, Any]


class FunctionResult(BaseModel):
    """Function execution result."""
    name: str
    result: Any
    error: Optional[str] = None
