"""AI instruction processing routes."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.dependencies import get_current_user
from src.core.logging import get_logger
from src.models.user import User
from src.services.llm_service import LLMService
from src.services.transformation_service import TransformationService, TransformationRule

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
        try:
            raw_rules = await llm_service.process_instruction(request.instruction, request.data)
            logger.info(f"LLM returned rules: {raw_rules}")
        except Exception as llm_error:
            logger.warning(f"LLM service failed: {llm_error}. Using fallback transformations.")
            # Fallback: create basic transformation based on instruction keywords
            raw_rules = []
            instruction_lower = request.instruction.lower()

            logger.info(f"Fallback triggered for instruction: {instruction_lower}")

            if "email" in instruction_lower or "emails" in instruction_lower:
                raw_rules.append(
                    {
                        "type": "extract",
                        "description": "Extract email addresses from text",
                        "parameters": {
                            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                        },
                    }
                )
            elif (
                "show" in instruction_lower
                or "extract" in instruction_lower
                or "get" in instruction_lower
            ) and any(field in instruction_lower for field in ["name", "email", "phone"]):
                # Fallback for filtering/extraction instructions
                logger.info(f"Fallback condition met for filtering: show/extract/get + field")
                fields = []
                if "name" in instruction_lower:
                    fields.append("name")
                if "email" in instruction_lower:
                    fields.append("email")
                if "phone" in instruction_lower:
                    fields.append("phone")

                logger.info(f"Extracted fields: {fields}")

                if fields:
                    raw_rules.append(
                        {
                            "type": "filter_content",
                            "description": f"Show only {', '.join(fields)} information",
                            "parameters": {"fields": fields},
                        }
                    )
            elif "phone" in instruction_lower or "number" in instruction_lower:
                raw_rules.append(
                    {
                        "type": "extract",
                        "description": "Extract phone numbers from text",
                        "parameters": {"pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"},
                    }
                )
            elif "uppercase" in instruction_lower or "upper" in instruction_lower:
                raw_rules.append(
                    {
                        "type": "transform",
                        "description": "Convert text to uppercase",
                        "parameters": {"operation": "uppercase"},
                    }
                )

        # Convert dictionary rules to TransformationRule objects
        transformation_rules = []
        for rule_dict in raw_rules:
            if isinstance(rule_dict, dict) and "type" in rule_dict:
                rule = TransformationRule(
                    operation=rule_dict.get("type", "unknown"),
                    parameters=rule_dict.get("parameters", {}),
                    description=rule_dict.get("description", ""),
                )
                transformation_rules.append(rule)

        # Apply transformations
        transformed_data = transformation_service.apply_transformations(
            request.data, transformation_rules
        )

        # Generate explanation
        if transformation_rules:
            explanation = f"Applied {len(transformation_rules)} transformations based on instruction: {request.instruction}"
        else:
            explanation = f"No specific transformations found for instruction: {request.instruction}. Data returned unchanged."

        return InstructionResponse(transformed_data=transformed_data, explanation=explanation)

    except Exception as e:
        logger.error(f"Error processing instruction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process instruction: {str(e)}")
