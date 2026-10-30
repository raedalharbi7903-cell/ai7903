"""Shared exact-origin defense; never an authentication or CORS permission."""

from fastapi import Request
from pydantic import AnyHttpUrl

from app.core.exceptions import APIError


def validate_private_origin(
    origin: AnyHttpUrl | None, environment: str, label: str
) -> None:
    if origin is None:
        return
    if (
        origin.username is not None
        or origin.password is not None
        or origin.path not in (None, "", "/")
        or origin.query is not None
        or origin.fragment is not None
        or not origin.host
        or "*" in origin.host
    ):
        raise ValueError(f"{label} origin must contain only scheme, host and port")
    if origin.scheme != "https" and (
        environment not in {"development", "testing"}
        or origin.host not in {"localhost", "127.0.0.1", "::1", "[::1]"}
    ):
        raise ValueError(f"{label} origin requires HTTPS outside loopback development")


def require_exact_origin(request: Request, allowed: AnyHttpUrl, code: str) -> None:
    origins = request.headers.getlist("origin")
    if (
        len(origins) != 1
        or origins[0] != str(allowed).rstrip("/")
        or request.headers.get("sec-fetch-site") == "cross-site"
    ):
        raise APIError(403, code, "Access denied")
