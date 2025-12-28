"""Batch job model for processing multiple files simultaneously."""

from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class BatchJob(BaseModel):
    """Model for batch file processing jobs."""

    __tablename__ = "batch_jobs"

    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # User-defined batch name
    status = Column(
        String(50), nullable=False, default="queued"
    )  # queued, processing, completed, failed
    total_files = Column(Integer, nullable=False, default=0)
    processed_files = Column(Integer, nullable=False, default=0)
    failed_files = Column(Integer, nullable=False, default=0)
    progress = Column(Float, nullable=False, default=0.0)  # 0-100
    estimated_cost = Column(Float, nullable=False, default=0.0)
    actual_cost = Column(Float, nullable=False, default=0.0)

    # Store file information as JSON
    files = Column(JSON, nullable=False, default=list)  # List of file metadata
    results = Column(JSON, nullable=True)  # Aggregated results
    errors = Column(JSON, nullable=True)  # File-specific errors

    # Relationships
    user = relationship("User", back_populates="batch_jobs")
    batch_files = relationship(
        "BatchFile", back_populates="batch_job", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<BatchJob(id={self.id}, name={self.name}, status={self.status}, progress={self.progress}%)>"


class BatchFile(BaseModel):
    """Model for individual files within a batch job."""

    __tablename__ = "batch_files"

    batch_job_id = Column(ForeignKey("batch_jobs.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    status = Column(
        String(50), nullable=False, default="queued"
    )  # queued, processing, completed, failed
    progress = Column(Float, nullable=False, default=0.0)  # 0-100
    current_step = Column(String(255), nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    aws_services_used = Column(JSON, nullable=False, default=list)
    cost_estimate = Column(Float, nullable=False, default=0.0)

    # Relationships
    batch_job = relationship("BatchJob", back_populates="batch_files")

    def __repr__(self):
        return f"<BatchFile(id={self.id}, filename={self.filename}, status={self.status})>"
