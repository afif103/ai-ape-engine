"""Code assistant service for code generation, review, and explanation."""

import logging

from src.llm.base import LLMMessage
from src.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class CodeService:
    """Service for AI-powered code assistance."""

    def __init__(self):
        """Initialize code service."""
        self.llm_service = get_llm_service()

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        context: str | None = None,
    ) -> dict:
        """Generate code from description.

        Args:
            description: What the code should do
            language: Programming language
            context: Optional additional context

        Returns:
            Dict with code, explanation, provider, model
        """
        system_prompt = f"""You are an expert {language} programmer.
Generate clean, well-documented code that follows best practices.
Include type hints (if applicable), error handling, and helpful comments."""

        user_prompt = f"""Generate {language} code for:
{description}

{f"Context: {context}" if context else ""}

Provide:
1. The code (in a code block)
2. Brief explanation of how it works
3. Usage example (if applicable)"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm_service.generate(messages)

        return {
            "content": response.content,
            "language": language,
            "provider": response.provider,
            "model": response.model,
        }

    async def review_code(
        self,
        code: str,
        language: str = "python",
        focus: str | None = None,
    ) -> dict:
        """Review code for issues and improvements.

        Args:
            code: Code to review
            language: Programming language
            focus: Optional focus area (security, performance, etc.)

        Returns:
            Dict with review, suggestions, provider, model
        """
        system_prompt = f"""You are an expert code reviewer for {language}.
Provide constructive feedback on code quality, bugs, and improvements.
Focus on: correctness, readability, efficiency, and best practices."""

        user_prompt = f"""Review this {language} code:

```{language}
{code}
```

{f"Focus particularly on: {focus}" if focus else ""}

Provide:
1. Overall assessment (Good/Needs Work/Poor)
2. Issues found (bugs, anti-patterns, inefficiencies)
3. Specific improvement suggestions
4. Positive aspects (what's done well)"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm_service.generate(messages)

        return {
            "review": response.content,
            "language": language,
            "provider": response.provider,
            "model": response.model,
        }

    async def explain_code(
        self,
        code: str,
        language: str = "python",
        level: str = "beginner",
    ) -> dict:
        """Explain what code does.

        Args:
            code: Code to explain
            language: Programming language
            level: Explanation level (beginner/intermediate/advanced)

        Returns:
            Dict with explanation, provider, model
        """
        system_prompt = f"""You are a patient programming teacher explaining {language} code.
Explain clearly for a {level} level programmer."""

        user_prompt = f"""Explain this {language} code in {level}-friendly terms:

```{language}
{code}
```

Provide:
1. What the code does (high-level purpose)
2. Step-by-step explanation of key parts
3. Concepts used (algorithms, patterns, etc.)
4. Example of when you'd use this"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm_service.generate(messages)

        return {
            "explanation": response.content,
            "language": language,
            "level": level,
            "provider": response.provider,
            "model": response.model,
        }

    async def fix_code(
        self,
        code: str,
        error: str,
        language: str = "python",
    ) -> dict:
        """Fix code based on error message.

        Args:
            code: Code with error
            error: Error message
            language: Programming language

        Returns:
            Dict with fixed_code, explanation, provider, model
        """
        system_prompt = f"""You are a debugging expert for {language}.
Analyze errors and provide working fixes."""

        user_prompt = f"""Fix this {language} code that's producing an error:

Code:
```{language}
{code}
```

Error:
```
{error}
```

Provide:
1. The fixed code (complete, working version)
2. Explanation of what was wrong
3. Why the fix works"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm_service.generate(messages)

        return {
            "result": response.content,
            "language": language,
            "provider": response.provider,
            "model": response.model,
        }
