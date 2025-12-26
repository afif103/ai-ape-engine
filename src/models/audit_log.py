"""Audit log model."""

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class AuditLog(BaseModel):
    """Audit log model for compliance tracking."""

    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(INET)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
