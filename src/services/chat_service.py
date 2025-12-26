"""Chat service for conversation management."""

import logging
from typing import AsyncIterator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.base import LLMMessage
from src.repositories.conversation_repository import ConversationRepository
from src.repositories.message_repository import MessageRepository
from src.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and AI responses."""

    def __init__(self, db: AsyncSession):
        """Initialize chat service.

        Args:
            db: Database session
        """
        self.db = db
        self.llm_service = get_llm_service()

    async def create_conversation(self, user_id: UUID, title: Optional[str] = None) -> UUID:
        """Create a new conversation.

        Args:
            user_id: User ID
            title: Optional conversation title

        Returns:
            Conversation ID
        """
        conversation = await ConversationRepository.create(self.db, user_id=user_id, title=title)
        return conversation.id

    async def send_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        content: str,
        context_messages: int = 10,
    ) -> dict:
        """Send a message and get AI response.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            context_messages: Number of previous messages to include in context

        Returns:
            Dict with user message, assistant message, provider, model

        Raises:
            ValueError: If conversation not found or user doesn't own it
        """
        # Verify ownership
        if not await ConversationRepository.verify_ownership(self.db, conversation_id, user_id):
            raise ValueError("Conversation not found or access denied")

        # Save user message
        user_message = await MessageRepository.create(
            self.db,
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        # Get conversation history
        history = await MessageRepository.get_conversation_messages(
            self.db, conversation_id, limit=context_messages
        )

        # Build LLM messages (excluding the just-added user message from history)
        llm_messages = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in history[:-1]  # Exclude last message (the one we just added)
        ]
        # Add the current user message
        llm_messages.append(LLMMessage(role="user", content=content))

        # Get AI response
        logger.info(f"Generating response for conversation {conversation_id}")
        response = await self.llm_service.generate(llm_messages)

        # Save assistant message
        assistant_message = await MessageRepository.create(
            self.db,
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "provider": response.provider,
            "model": response.model,
        }

    async def stream_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        content: str,
        context_messages: int = 10,
    ) -> AsyncIterator[str]:
        """Send a message and stream AI response.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            context_messages: Number of previous messages to include

        Yields:
            Chunks of AI response

        Raises:
            ValueError: If conversation not found or access denied
        """
        # Verify ownership
        if not await ConversationRepository.verify_ownership(self.db, conversation_id, user_id):
            raise ValueError("Conversation not found or access denied")

        # Save user message
        await MessageRepository.create(
            self.db,
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        # Get conversation history
        history = await MessageRepository.get_conversation_messages(
            self.db, conversation_id, limit=context_messages
        )

        # Build LLM messages
        llm_messages = [LLMMessage(role=msg.role, content=msg.content) for msg in history]

        # Stream AI response
        full_response = ""
        async for chunk in self.llm_service.stream(llm_messages):
            full_response += chunk
            yield chunk

        # Save complete assistant message after streaming
        await MessageRepository.create(
            self.db,
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
        )

    async def get_conversation_with_messages(self, conversation_id: UUID, user_id: UUID) -> dict:
        """Get conversation with messages and stats.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Dict with conversation, messages, token_stats

        Raises:
            ValueError: If conversation not found or access denied
        """
        # Verify ownership
        if not await ConversationRepository.verify_ownership(self.db, conversation_id, user_id):
            raise ValueError("Conversation not found or access denied")

        conversation = await ConversationRepository.get_by_id(self.db, conversation_id)
        messages = await MessageRepository.get_conversation_messages(self.db, conversation_id)
        token_stats = await MessageRepository.get_token_count(self.db, conversation_id)

        return {
            "conversation": conversation,
            "messages": messages,
            "token_stats": token_stats,
        }

    async def list_conversations(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list:
        """List user's conversations.

        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Number to skip

        Returns:
            List of conversations
        """
        return await ConversationRepository.get_user_conversations(
            self.db, user_id, limit=limit, offset=offset
        )

    async def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Delete a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            True if deleted, False otherwise

        Raises:
            ValueError: If conversation not found or access denied
        """
        # Verify ownership
        if not await ConversationRepository.verify_ownership(self.db, conversation_id, user_id):
            raise ValueError("Conversation not found or access denied")

        return await ConversationRepository.delete(self.db, conversation_id)
