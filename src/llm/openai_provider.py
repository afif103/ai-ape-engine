"""OpenAI LLM provider implementation."""

import logging
from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider.

    Fallback provider for when Groq or Bedrock are unavailable.
    Reliable and widely supported.

    Supported models:
    - gpt-4o-mini (fast, cost-effective, recommended fallback)
    - gpt-4o (most capable)
    - gpt-3.5-turbo (legacy, cheaper)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        super().__init__(model, temperature, max_tokens)
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI provider with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    def supports_streaming(self) -> bool:
        """OpenAI supports streaming."""
        return True

    async def generate(self, messages: list[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a response using OpenAI.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Override defaults with kwargs
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response
            choice = response.choices[0]
            content = choice.message.content or ""

            # Extract token usage
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            logger.debug(
                f"OpenAI generate: {total_tokens} tokens (in={input_tokens}, out={output_tokens})"
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
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def stream(self, messages: list[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream a response using OpenAI.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text

        Raises:
            Exception: If OpenAI streaming fails
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Override defaults with kwargs
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            # Stream from OpenAI
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.debug("OpenAI stream completed")

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
