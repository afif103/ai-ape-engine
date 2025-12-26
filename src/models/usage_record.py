"""Usage record model."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class UsageRecord(BaseModel):
    """Usage tracking model for cost monitoring."""

    __tablename__ = "usage_records"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service = Column(String(50), nullable=False)  # chat, research, extraction, code
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6))

    # Relationships
    user = relationship("User", back_populates="usage_records")
