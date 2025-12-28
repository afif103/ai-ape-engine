"""Multi-provider LLM service with automatic fallback."""

import logging
from typing import Any, AsyncIterator, Optional

from src.config import get_settings
from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from src.llm.bedrock_provider import BedrockProvider
from src.llm.groq_provider import GroqProvider
from src.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMService:
    """Multi-provider LLM service with automatic fallback.

    Tries providers in order:
    1. Groq (fast, cheap, good for development)
    2. AWS Bedrock (production-grade, Claude)
    3. OpenAI (reliable fallback)

    If a provider fails, automatically tries the next one.
    This ensures high availability even if one service is down.

    Usage:
        service = LLMService()
        response = await service.generate([
            LLMMessage(role="user", content="Hello!")
        ])
    """

    def __init__(self):
        """Initialize LLM service with available providers."""
        settings = get_settings()
        self.providers: list[BaseLLMProvider] = []

        # Initialize Groq if API key available
        if settings.groq_api_key:
            try:
                groq = GroqProvider(
                    api_key=settings.groq_api_key,
                    model="llama-3.1-8b-instant",
                )
                self.providers.append(groq)
                logger.info("Groq provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")

        # Initialize Bedrock if AWS credentials available
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                bedrock = BedrockProvider(
                    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
                    region_name=settings.aws_default_region,
                )
                self.providers.append(bedrock)
                logger.info("Bedrock provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock: {e}")

        # Initialize OpenAI if API key available
        if settings.openai_api_key:
            try:
                openai = OpenAIProvider(api_key=settings.openai_api_key, model="gpt-4o-mini")
                self.providers.append(openai)
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")

        if not self.providers:
            raise ValueError(
                "No LLM providers available. Please configure at least one: "
                "GROQ_API_KEY, AWS credentials, or OPENAI_API_KEY"
            )

        logger.info(f"LLM service initialized with {len(self.providers)} provider(s)")

    async def generate(self, messages: list[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a response using first available provider.

        Tries providers in order until one succeeds.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments (temperature, max_tokens, etc.)

        Returns:
            LLMResponse from successful provider

        Raises:
            Exception: If all providers fail
        """
        last_error = None

        for provider in self.providers:
            try:
                logger.debug(f"Trying provider: {provider.provider_name}")
                response = await provider.generate(messages, **kwargs)
                logger.info(f"Successfully generated response using {provider.provider_name}")
                return response

            except Exception as e:
                logger.warning(
                    f"Provider {provider.provider_name} failed: {e}. Trying next provider..."
                )
                last_error = e
                continue

        # All providers failed
        error_msg = f"All {len(self.providers)} LLM provider(s) failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def stream(self, messages: list[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream a response using first available provider.

        Tries providers in order until one succeeds.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text

        Raises:
            Exception: If all providers fail
        """
        last_error = None

        for provider in self.providers:
            try:
                logger.debug(f"Trying stream provider: {provider.provider_name}")

                async for chunk in provider.stream(messages, **kwargs):
                    yield chunk

                logger.info(f"Successfully streamed using {provider.provider_name}")
                return  # Success, exit

            except Exception as e:
                logger.warning(
                    f"Stream provider {provider.provider_name} failed: {e}. Trying next provider..."
                )
                last_error = e
                continue

        # All providers failed
        error_msg = (
            f"All {len(self.providers)} LLM provider(s) failed for streaming. "
            f"Last error: {last_error}"
        )
        logger.error(error_msg)
        raise Exception(error_msg)

    def get_available_providers(self) -> list[str]:
        """Get list of available provider names.

        Returns:
            List of provider names (e.g., ["groq", "bedrock"])
        """
        return [p.provider_name for p in self.providers]

    async def process_instruction(self, instruction: str, data: Any) -> list[dict]:
        """Process natural language instruction to generate data transformation rules.

        Args:
            instruction: Natural language instruction (e.g., "extract email addresses")
            data: The data to be transformed

        Returns:
            List of transformation rules that can be applied to the data
        """
        # Create a prompt that explains the data and asks for transformation rules
        data_preview = self._create_data_preview(data)

        prompt = f"""You are an AI assistant that converts natural language instructions into data transformation rules.

DATA TO TRANSFORM:
{data_preview}

INSTRUCTION: {instruction}

Analyze the instruction and determine its type:
- EXTRACTION: Find and extract specific patterns (emails, phones, names)
- FILTERING: Show only specific content or hide unwanted parts
- TRANSFORMATION: Modify existing data (uppercase, format changes)

Return ONLY a JSON array of transformation objects. No explanations, no markdown, just JSON.

Format: [{{"type": "operation_name", "description": "what it does", "parameters": {{"key": "value"}}}}]

Examples:
- "extract email addresses": [{{"type": "extract", "description": "Extract email addresses", "parameters": {{"pattern": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{(2,)}\\b"}}}}]
- "show only name and email": [{{"type": "filter_content", "description": "Show only name and email information", "parameters": {{"fields": ["name", "email"]}}}}]
- "show email": [{{"type": "filter_content", "description": "Show only email information", "parameters": {{"fields": ["email"]}}}}]
- "convert to uppercase": [{{"type": "transform", "description": "Convert text to uppercase", "parameters": {{"operation": "uppercase"}}}}]
- "remove phone numbers": [{{"type": "filter_content", "description": "Hide phone number information", "parameters": {{"exclude_fields": ["phone"]}}}}]

If no transformations apply, return: []"""

        messages = [LLMMessage(role="user", content=prompt)]

        try:
            response = await self.generate(messages, temperature=0.1, max_tokens=1000)

            # Try to parse the response as JSON
            import json
            import re

            content = response.content.strip()

            # Try to extract JSON array from the response
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            try:
                transformations = json.loads(content)
                if isinstance(transformations, list):
                    return transformations
                else:
                    logger.warning(f"LLM returned non-array response: {content}")
                    return []
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM response as JSON: {content}, Error: {e}")
                return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON: {response.content}")
                return []

        except Exception as e:
            logger.error(f"Error processing instruction: {e}")
            return []

    def _create_data_preview(self, data: Any) -> str:
        """Create a preview of the data for the LLM prompt.

        Args:
            data: The data to preview

        Returns:
            String representation of the data
        """
        if isinstance(data, dict):
            preview_parts = []

            # Add text preview
            if "text" in data and data["text"]:
                text_preview = (
                    data["text"][:500] + "..." if len(data["text"]) > 500 else data["text"]
                )
                preview_parts.append(f"TEXT CONTENT:\n{text_preview}")

            # Add table preview
            if "tables" in data and data["tables"]:
                table = data["tables"][0]  # Preview first table
                preview_parts.append(
                    f"TABLE DATA ({len(table.get('rows', []))} rows, {len(table.get('columns', []))} columns):"
                )
                preview_parts.append(f"Columns: {', '.join(table.get('columns', []))}")

                # Show first few rows
                rows = table.get("rows", [])[:3]
                for i, row in enumerate(rows):
                    preview_parts.append(f"Row {i + 1}: {row}")

                if len(table.get("rows", [])) > 3:
                    preview_parts.append(f"... and {len(table.get('rows', [])) - 3} more rows")

            return "\n\n".join(preview_parts)

        return str(data)[:1000]  # Fallback for other data types


# Global service instance (lazy loaded)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance.

    Returns:
        Singleton LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
