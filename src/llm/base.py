"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Message for LLM conversation."""

    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(BaseModel):
    """Response from LLM provider."""

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Providers must implement:
    - generate(): Generate a response from messages
    - stream(): Stream a response (optional, can use generate as fallback)

    This allows seamless switching between Groq, Bedrock, OpenAI, etc.
    """

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        """Initialize provider.

        Args:
            model: Model identifier (e.g., "llama-3.1-8b-instant")
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate(self, messages: list[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a response from messages.

        Args:
            messages: List of conversation messages
            **kwargs: Provider-specific arguments

        Returns:
            LLMResponse with generated content and token counts

        Raises:
            Exception: If generation fails
        """
        pass

    async def stream(self, messages: list[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream a response from messages.

        Default implementation uses generate() and yields the full response.
        Providers can override for true streaming support.

        Args:
            messages: List of conversation messages
            **kwargs: Provider-specific arguments

        Yields:
            Chunks of generated text

        Raises:
            Exception: If streaming fails
        """
        response = await self.generate(messages, **kwargs)
        yield response.content

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name (e.g., 'groq', 'bedrock', 'openai')."""
        pass

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming.

        Returns:
            True if provider has native streaming support
        """
        return False
