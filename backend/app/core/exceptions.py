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
