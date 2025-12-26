"""Message model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Message(BaseModel):
    """Message model for chat messages."""

    __tablename__ = "messages"

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(50))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    @property
    def input_tokens(self) -> int:
        """Alias for tokens_used (for backward compatibility)."""
        return 0  # User messages don't consume input tokens from our perspective

    @property
    def output_tokens(self) -> int:
        """Get output tokens (assistant messages use tokens)."""
        return self.tokens_used if self.role == "assistant" else 0
