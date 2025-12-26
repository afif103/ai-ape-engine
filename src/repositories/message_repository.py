"""Message repository for chat operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.message import Message


class MessageRepository:
    """Repository for message database operations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> Message:
        """Create a new message.

        Args:
            db: Database session
            conversation_id: ID of conversation
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            input_tokens: Number of input tokens (for tracking)
            output_tokens: Number of output tokens (stored in tokens_used)

        Returns:
            Created message
        """
        # Store total tokens in tokens_used field
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=input_tokens + output_tokens,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession, conversation_id: UUID, limit: int | None = None
    ) -> list[Message]:
        """Get all messages in a conversation (chronological order).

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Optional maximum number of recent messages to return

        Returns:
            List of messages
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )

        if limit:
            # Get most recent N messages, but return them in chronological order
            # First get most recent IDs
            subquery = (
                select(Message.id)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            result = await db.execute(subquery)
            message_ids = [row[0] for row in result.all()]

            # Then get those messages in chronological order
            query = select(Message).where(Message.id.in_(message_ids)).order_by(Message.created_at)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, message_id: UUID) -> Message | None:
        """Get message by ID.

        Args:
            db: Database session
            message_id: Message ID

        Returns:
            Message if found, None otherwise
        """
        result = await db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_token_count(db: AsyncSession, conversation_id: UUID) -> dict:
        """Get total token count for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Dict with input_tokens, output_tokens, total_tokens
        """
        messages = await MessageRepository.get_conversation_messages(db, conversation_id)

        # Calculate totals using properties
        input_tokens = sum(m.input_tokens for m in messages)
        output_tokens = sum(m.output_tokens for m in messages)
        total_tokens = sum(m.tokens_used or 0 for m in messages)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "message_count": len(messages),
        }
