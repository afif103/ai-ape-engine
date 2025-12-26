"""AI instruction processing routes."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.dependencies import get_current_user
from src.core.logging import get_logger
from src.models.user import User
from src.services.llm_service import LLMService
from src.services.transformation_service import TransformationService

logger = get_logger(__name__)
router = APIRouter()

llm_service = LLMService()
transformation_service = TransformationService()


class InstructionRequest(BaseModel):
    """Request model for AI instruction processing."""

    instruction: str
    data: Dict[str, Any]


class InstructionResponse(BaseModel):
    """Response model for AI instruction processing."""

    transformed_data: Dict[str, Any]
    explanation: str


@router.post("/instruction/process", response_model=InstructionResponse)
async def process_instruction(
    request: InstructionRequest, current_user: User = Depends(get_current_user)
) -> InstructionResponse:
    """Process natural language instruction to transform data.

    Args:
        request: Instruction and data to process
        current_user: Authenticated user

    Returns:
        Transformed data and explanation
    """
    try:
        logger.info(
            f"Processing instruction for user {current_user.id}: {request.instruction[:50]}..."
        )

        # Use LLM to convert natural language instruction to transformation rules
        transformation_rules = await llm_service.process_instruction(
            request.instruction, request.data
        )

        # Apply transformations
        transformed_data = transformation_service.apply_transformations(
            request.data, transformation_rules
        )

        # Generate explanation
        explanation = f"Applied {len(transformation_rules)} transformations based on instruction: {request.instruction}"

        return InstructionResponse(transformed_data=transformed_data, explanation=explanation)

    except Exception as e:
        logger.error(f"Error processing instruction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process instruction: {str(e)}")
