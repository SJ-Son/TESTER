"""Custom exceptions for the TESTER application."""


class TesterException(Exception):
    """Base exception for all TESTER-specific errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(TesterException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class TurnstileError(TesterException):
    """Raised when Cloudflare Turnstile verification fails."""

    def __init__(self, message: str = "Bot detection failed"):
        super().__init__(message, code="TURNSTILE_FAILED")


class GenerationError(TesterException):
    """Raised when AI code generation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="GENERATION_ERROR")


class AuthenticationError(TesterException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_ERROR")
