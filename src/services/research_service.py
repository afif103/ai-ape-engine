"""Research service using Firecrawl for web scraping."""

import logging
from typing import Any

from firecrawl import FirecrawlApp

from src.config import get_settings
from src.llm.base import LLMMessage
from src.services.llm_service import get_llm_service

try:
    import PyPDF2

    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document

    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for AI-powered web research."""

    def __init__(self):
        """Initialize research service."""
        settings = get_settings()
        self.firecrawl = (
            FirecrawlApp(api_key=settings.firecrawl_api_key) if settings.firecrawl_api_key else None
        )
        self.llm_service = get_llm_service()

    async def scrape_url(self, url: str) -> dict:
        """Scrape content from a single URL.

        Args:
            url: URL to scrape

        Returns:
            Dict with markdown content and metadata
        """
        if not self.firecrawl:
            raise ValueError("Firecrawl API key not configured")

        try:
            result = self.firecrawl.scrape(url)
            return {
                "url": url,
                "content": result.markdown or "",
                "metadata": result.metadata or {},
            }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    async def process_file(self, file_content: bytes, filename: str) -> dict:
        """Process uploaded file and extract text content.

        Args:
            file_content: Raw file bytes
            filename: Original filename

        Returns:
            Dict with extracted text and metadata
        """
        try:
            text_content = ""

            if filename.lower().endswith(".pdf") and HAS_PDF:
                # Process PDF
                from io import BytesIO

                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"

            elif filename.lower().endswith(".docx") and HAS_DOCX:
                # Process DOCX
                from io import BytesIO

                doc = Document(BytesIO(file_content))
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"

            elif filename.lower().endswith(".txt"):
                # Process plain text
                text_content = file_content.decode("utf-8", errors="ignore")

            else:
                # Try to decode as text
                text_content = file_content.decode("utf-8", errors="ignore")

            return {
                "filename": filename,
                "content": text_content.strip(),
                "word_count": len(text_content.split()),
                "file_type": filename.split(".")[-1].lower() if "." in filename else "unknown",
            }

        except Exception as e:
            logger.error(f"Failed to process file {filename}: {e}")
            raise ValueError(f"Failed to process file: {str(e)}")

    async def research_topic(
        self,
        query: str,
        urls: list[str] | None = None,
        max_sources: int = 5,
    ) -> dict:
        """Research a topic using web sources and AI synthesis.

        Args:
            query: Research question
            urls: Optional list of specific URLs to research
            max_sources: Maximum number of sources to use

        Returns:
            Dict with synthesis, sources, provider, model
        """
        sources = []

        # Scrape provided URLs
        if urls:
            for url in urls[:max_sources]:
                try:
                    source = await self.scrape_url(url)
                    sources.append(source)
                except Exception as e:
                    logger.warning(f"Skipping {url}: {e}")

        if not sources:
            raise ValueError("No sources available for research")

        # Build context from sources
        context = "\n\n---\n\n".join(
            [
                f"Source {i + 1}: {s['url']}\n\n{s['content'][:2000]}"  # Limit content length
                for i, s in enumerate(sources)
            ]
        )

        # Synthesize research with AI
        system_prompt = """You are a research assistant. Synthesize information from sources to answer questions.
Cite sources in your answer. Be accurate and comprehensive."""

        user_prompt = f"""Research Question: {query}

Sources:
{context}

Provide a comprehensive answer that:
1. Directly answers the question
2. Synthesizes information from sources
3. Cites sources (mention "Source 1", "Source 2", etc.)
4. Notes any gaps or limitations in the available information"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm_service.generate(messages)

        return {
            "query": query,
            "synthesis": response.content,
            "sources": [
                {"url": s["url"], "title": getattr(s.get("metadata"), "title", "Untitled")}
                for s in sources
            ],
            "provider": response.provider,
            "model": response.model,
        }
