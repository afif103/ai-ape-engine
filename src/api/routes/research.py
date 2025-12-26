"""Research API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field, HttpUrl

from src.dependencies import CurrentUser
from src.services.research_service import ResearchService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    """Request for research."""

    query: str = Field(..., min_length=10, max_length=5000)
    urls: list[HttpUrl] | None = Field(None, max_items=10)
    max_sources: int = Field(default=5, ge=1, le=10)


class ScrapeRequest(BaseModel):
    """Request for URL scraping."""

    url: HttpUrl


@router.post("/scrape")
async def scrape_url(data: ScrapeRequest, user: CurrentUser):
    """Scrape content from a single URL."""
    try:
        research_service = ResearchService()
        result = await research_service.scrape_url(str(data.url))
        return result
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/topic")
async def research_topic(data: ResearchRequest, user: CurrentUser):
    """Research a topic using multiple web sources."""
    try:
        research_service = ResearchService()
        result = await research_service.research_topic(
            query=data.query,
            urls=[str(url) for url in data.urls] if data.urls else None,
            max_sources=data.max_sources,
        )
        return result
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a document file."""
    try:
        # Validate file type
        allowed_types = [
            "text/plain",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not supported. Please upload .txt, .pdf, or .docx files.",
            )

        # Read file content
        content = await file.read()

        # Process file
        research_service = ResearchService()
        result = await research_service.process_file(content, file.filename)

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File processing failed"
        )
