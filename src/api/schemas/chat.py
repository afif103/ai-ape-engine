"""Chat API request and response schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Request schema for creating a message."""

    content: str = Field(..., min_length=1, max_length=50000, description="Message content")


class MessageResponse(BaseModel):
    """Response schema for a message."""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    input_tokens: int
    output_tokens: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation."""

    title: Optional[str] = Field(None, max_length=500, description="Optional conversation title")


class ConversationResponse(BaseModel):
    """Response schema for a conversation."""

    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Response schema for conversation with messages."""

    messages: list[MessageResponse]
    token_stats: dict


class ChatResponse(BaseModel):
    """Response schema for chat completion."""

    message: MessageResponse
    provider: str
    model: str
