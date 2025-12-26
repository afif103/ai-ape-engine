"""Code assistant API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.dependencies import CurrentUser
from src.services.code_service import CodeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/code", tags=["code"])


class CodeGenerateRequest(BaseModel):
    """Request for code generation."""

    description: str = Field(..., min_length=10, max_length=5000)
    language: str = Field(default="python", max_length=50)
    context: str | None = Field(None, max_length=5000)


class CodeReviewRequest(BaseModel):
    """Request for code review."""

    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="python", max_length=50)
    focus: str | None = Field(None, max_length=500)


class CodeExplainRequest(BaseModel):
    """Request for code explanation."""

    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="python", max_length=50)
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")


class CodeFixRequest(BaseModel):
    """Request for code fix."""

    code: str = Field(..., min_length=1, max_length=50000)
    error: str = Field(..., min_length=1, max_length=10000)
    language: str = Field(default="python", max_length=50)


@router.post("/generate")
async def generate_code(data: CodeGenerateRequest, user: CurrentUser):
    """Generate code from description."""
    try:
        code_service = CodeService()
        result = await code_service.generate_code(
            description=data.description,
            language=data.language,
            context=data.context,
        )
        return result
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/review")
async def review_code(data: CodeReviewRequest, user: CurrentUser):
    """Review code for issues."""
    try:
        code_service = CodeService()
        result = await code_service.review_code(
            code=data.code,
            language=data.language,
            focus=data.focus,
        )
        return result
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/explain")
async def explain_code(data: CodeExplainRequest, user: CurrentUser):
    """Explain what code does."""
    try:
        code_service = CodeService()
        result = await code_service.explain_code(
            code=data.code,
            language=data.language,
            level=data.level,
        )
        return result
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/fix")
async def fix_code(data: CodeFixRequest, user: CurrentUser):
    """Fix code based on error."""
    try:
        code_service = CodeService()
        result = await code_service.fix_code(
            code=data.code,
            error=data.error,
            language=data.language,
        )
        return result
    except Exception as e:
        logger.error(f"Code fix failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
