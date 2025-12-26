"""Custom exceptions for APE."""


class APEException(Exception):
    """Base exception for all APE errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APEException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(APEException):
    """Raised when user lacks permissions."""

    pass


class ValidationError(APEException):
    """Raised when input validation fails."""

    pass


class NotFoundError(APEException):
    """Raised when resource is not found."""

    pass


class RateLimitError(APEException):
    """Raised when rate limit is exceeded."""

    pass


class LLMProviderError(APEException):
    """Raised when LLM provider fails."""

    pass


class ExternalServiceError(APEException):
    """Raised when external service fails."""

    pass


class DatabaseError(APEException):
    """Raised when database operation fails."""

    pass
