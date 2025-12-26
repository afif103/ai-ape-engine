"""Conversation repository for chat operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation


class ConversationRepository:
    """Repository for conversation database operations."""

    @staticmethod
    async def create(db: AsyncSession, user_id: UUID, title: Optional[str] = None) -> Conversation:
        """Create a new conversation.

        Args:
            db: Database session
            user_id: ID of user creating conversation
            title: Optional conversation title

        Returns:
            Created conversation
        """
        conversation = Conversation(user_id=user_id, title=title or "New Conversation")
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation if found, None otherwise
        """
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_conversations(
        db: AsyncSession, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        """Get user's conversations (most recent first).

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations
        """
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_title(
        db: AsyncSession, conversation_id: UUID, title: str
    ) -> Optional[Conversation]:
        """Update conversation title.

        Args:
            db: Database session
            conversation_id: Conversation ID
            title: New title

        Returns:
            Updated conversation if found, None otherwise
        """
        conversation = await ConversationRepository.get_by_id(db, conversation_id)
        if conversation:
            conversation.title = title
            await db.commit()
            await db.refresh(conversation)
        return conversation

    @staticmethod
    async def delete(db: AsyncSession, conversation_id: UUID) -> bool:
        """Delete a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        conversation = await ConversationRepository.get_by_id(db, conversation_id)
        if conversation:
            await db.delete(conversation)
            await db.commit()
            return True
        return False

    @staticmethod
    async def verify_ownership(db: AsyncSession, conversation_id: UUID, user_id: UUID) -> bool:
        """Verify user owns conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            True if user owns conversation, False otherwise
        """
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None
