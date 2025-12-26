"""AWS Bedrock LLM provider implementation."""

import json
import logging
from typing import Any, AsyncIterator

import boto3

from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class BedrockProvider(BaseLLMProvider):
    """AWS Bedrock LLM provider.

    Uses AWS Bedrock for production-grade LLM calls with enterprise features:
    - Guardrails for content filtering and PII detection
    - High availability and scalability
    - Integration with AWS services

    Supported models:
    - anthropic.claude-3-5-sonnet-20241022-v2:0 (recommended for production)
    - anthropic.claude-3-haiku-20240307-v1:0 (fast, cost-effective)
    """

    def __init__(
        self,
        model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        region_name: str = "us-east-1",
        guardrail_id: str | None = None,
        guardrail_version: str = "DRAFT",
    ):
        """Initialize Bedrock provider.

        Args:
            model: Bedrock model ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            region_name: AWS region
            guardrail_id: Optional guardrail ID for content filtering
            guardrail_version: Guardrail version
        """
        super().__init__(model, temperature, max_tokens)
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        logger.info(f"Initialized Bedrock provider with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "bedrock"

    def supports_streaming(self) -> bool:
        """Bedrock supports streaming."""
        return True

    def _convert_messages(self, messages: list[LLMMessage]) -> tuple[str, list[dict]]:
        """Convert LLMMessage format to Claude format.

        Claude expects:
        - System message separate
        - Messages as alternating user/assistant

        Args:
            messages: List of LLMMessage objects

        Returns:
            Tuple of (system_message, claude_messages)
        """
        system_message = ""
        claude_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                claude_messages.append({"role": msg.role, "content": msg.content})

        return system_message, claude_messages

    async def generate(self, messages: list[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a response using Bedrock.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If Bedrock API call fails
        """
        try:
            # Convert messages to Claude format
            system_message, claude_messages = self._convert_messages(messages)

            # Build request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": claude_messages,
            }

            if system_message:
                body["system"] = system_message

            # Add guardrails if configured
            invoke_kwargs = {"modelId": self.model, "body": json.dumps(body)}

            if self.guardrail_id:
                invoke_kwargs["guardrailIdentifier"] = self.guardrail_id
                invoke_kwargs["guardrailVersion"] = self.guardrail_version

            # Call Bedrock
            response = self.client.invoke_model(**invoke_kwargs)

            # Parse response
            response_body = json.loads(response["body"].read())

            content = response_body["content"][0]["text"]
            input_tokens = response_body["usage"]["input_tokens"]
            output_tokens = response_body["usage"]["output_tokens"]
            total_tokens = input_tokens + output_tokens

            logger.debug(
                f"Bedrock generate: {total_tokens} tokens (in={input_tokens}, out={output_tokens})"
            )

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                finish_reason=response_body.get("stop_reason"),
            )

        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            raise

    async def stream(self, messages: list[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream a response using Bedrock.

        Args:
            messages: Conversation messages
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text

        Raises:
            Exception: If Bedrock streaming fails
        """
        try:
            # Convert messages to Claude format
            system_message, claude_messages = self._convert_messages(messages)

            # Build request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": claude_messages,
            }

            if system_message:
                body["system"] = system_message

            # Stream from Bedrock
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model, body=json.dumps(body)
            )

            # Process stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        chunk_data = json.loads(chunk.get("bytes").decode())

                        # Extract content delta
                        if chunk_data["type"] == "content_block_delta":
                            delta = chunk_data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta["text"]

            logger.debug("Bedrock stream completed")

        except Exception as e:
            logger.error(f"Bedrock streaming failed: {e}")
            raise
