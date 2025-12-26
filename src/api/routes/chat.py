"""Chat API endpoints."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat import (
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
)
from src.dependencies import CurrentUser, DatabaseSession
from src.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    data: ConversationCreate,
    user: CurrentUser,
    db: DatabaseSession,
):
    """Create a new conversation."""
    try:
        chat_service = ChatService(db)
        conversation_id = await chat_service.create_conversation(user_id=user.id, title=data.title)

        # Get the created conversation
        result = await chat_service.get_conversation_with_messages(conversation_id, user.id)
        return result["conversation"]

    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user: CurrentUser,
    db: DatabaseSession,
    limit: int = 50,
    offset: int = 0,
):
    """List user's conversations."""
    try:
        chat_service = ChatService(db)
        conversations = await chat_service.list_conversations(user.id, limit=limit, offset=offset)
        return conversations

    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    user: CurrentUser,
    db: DatabaseSession,
):
    """Get conversation with messages."""
    try:
        chat_service = ChatService(db)
        result = await chat_service.get_conversation_with_messages(conversation_id, user.id)
        return {
            **result["conversation"].__dict__,
            "messages": result["messages"],
            "token_stats": result["token_stats"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation",
        )


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: UUID,
    data: MessageCreate,
    user: CurrentUser,
    db: DatabaseSession,
):
    """Send a message and get AI response."""
    try:
        chat_service = ChatService(db)
        result = await chat_service.send_message(conversation_id, user.id, data.content)

        return ChatResponse(
            message=MessageResponse.model_validate(result["assistant_message"]),
            provider=result["provider"],
            model=result["model"],
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: UUID,
    data: MessageCreate,
    user: CurrentUser,
    db: DatabaseSession,
):
    """Stream AI response for a message."""
    try:
        chat_service = ChatService(db)

        async def generate():
            try:
                async for chunk in chat_service.stream_message(
                    conversation_id, user.id, data.content
                ):
                    # Escape the chunk for JSON
                    escaped_chunk = (
                        chunk.replace("\\", "\\\\")
                        .replace('"', '\\"')
                        .replace("\n", "\\n")
                        .replace("\r", "\\r")
                    )
                    yield f'data: {{"content": "{escaped_chunk}"}}\n\n'
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f'data: {{"error": "{str(e)}"}}\n\n'

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stream message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream message",
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    user: CurrentUser,
    db: DatabaseSession,
):
    """Delete a conversation."""
    try:
        chat_service = ChatService(db)
        deleted = await chat_service.delete_conversation(conversation_id, user.id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )
