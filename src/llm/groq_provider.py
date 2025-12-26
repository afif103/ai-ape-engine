"""Groq LLM provider implementation."""

import logging
from typing import Any, AsyncIterator

from groq import AsyncGroq

from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider.

    Uses Groq's high-speed inference for fast, cost-effective LLM calls.
    Ideal for development and high-throughput production workloads.

    Supported models:
    - llama-3.1-8b-instant (recommended for development)
    - llama-3.1-70b-versatile (more capable, slightly slower)
    - mixtral-8x7b-32768 (large context window)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        super().__init__(model, temperature, max_tokens)
        self.client = AsyncGroq(api_key=api_key)
        logger.info(f"Initialized Groq provider with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "groq"

    def supports_streaming(self) -> bool:
        """Groq supports streaming."""
        return True

    async def generate(self, messages: list[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a response using Groq.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If Groq API call fails
        """
        try:
            # Convert messages to Groq format
            groq_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Override defaults with kwargs
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            # Call Groq API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response
            choice = response.choices[0]
            content = choice.message.content

            # Extract token usage
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            logger.debug(
                f"Groq generate: {total_tokens} tokens (in={input_tokens}, out={output_tokens})"
            )

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                finish_reason=choice.finish_reason,
            )

        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise

    async def stream(self, messages: list[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream a response using Groq.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text

        Raises:
            Exception: If Groq streaming fails
        """
        try:
            # Convert messages to Groq format
            groq_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Override defaults with kwargs
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            # Stream from Groq
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.debug(f"Groq stream completed")

        except Exception as e:
            logger.error(f"Groq streaming failed: {e}")
            raise
