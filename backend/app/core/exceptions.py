from typing import Any


class APIError(Exception):
    """Intentional API error with a consistent response contract."""

    def __init__(
        self, status_code: int, code: str, message: str, details: Any | None = None
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class ResourceNotFoundError(APIError):
    """Raised when a requested resource cannot be found."""

    def __init__(self, resource: str) -> None:
        super().__init__(404, "resource_not_found", f"{resource} was not found")


class ConflictError(APIError):
    """Raised when an operation conflicts with existing state."""

    def __init__(self, message: str) -> None:
        super().__init__(409, "conflict", message)
