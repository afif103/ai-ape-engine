"""User model."""

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class User(BaseModel):
    """User account model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    research_sessions = relationship(
        "ResearchSession", back_populates="user", cascade="all, delete-orphan"
    )
    extraction_jobs = relationship(
        "ExtractionJob", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="user", cascade="all, delete-orphan")
