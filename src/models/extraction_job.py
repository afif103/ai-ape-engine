"""Extraction job model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class ExtractionJob(BaseModel):
    """Data extraction job model."""

    __tablename__ = "extraction_jobs"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type = Column(String(20), nullable=False)  # document, web_single, web_crawl
    source_url = Column(Text)
    source_file_path = Column(Text)
    schema_definition = Column(JSONB, nullable=False)  # User-defined schema
    validation_rules = Column(JSONB)  # Validation rules for data
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    result_data = Column(JSONB)  # Extracted data
    error_message = Column(Text)
    rows_extracted = Column(Integer, default=0)
    rows_valid = Column(Integer, default=0)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="extraction_jobs")
