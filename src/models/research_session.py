"""Research session model."""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class ResearchSession(BaseModel):
    """Research session model."""

    __tablename__ = "research_sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    query = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    summary = Column(Text)
    sources = Column(JSONB)  # List of sources with URLs and content
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="research_sessions")
