import inspect
from functools import wraps
from flask import request, g
import jwt

from .database import get_db
from .models import Faculty
from .security import decode_token


class APIError(Exception):
    """Custom exception that translates directly to standard JSON HTTP responses."""
    def __init__(self, detail, status_code: int = 400):
        super().__init__(str(detail))
        self.detail = detail
        self.status_code = status_code


def get_token_from_header() -> str | None:
    """Extract Bearer token from request Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_user_from_request() -> Faculty:
    """
    Validates the Bearer token and returns the authenticated Faculty instance.
    Raises APIError with 401 or 403 on validation failure.
    """
    token = get_token_from_header()
    if not token:
        raise APIError("Not authenticated", 401)

    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise APIError("Invalid or expired token", 401)

    db = get_db()
    user = db.get(Faculty, user_id)
    if not user:
        raise APIError("User not found", 401)

    if not user.active:
        raise APIError("User account is inactive", 403)

    return user


def current_user(f):
    """
    Flask decorator: requires a valid JWT Bearer token and active user account.
    Injects the authenticated user into function kwargs (if accepted) and flask.g.current_user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user_from_request()
        g.current_user = user
        sig = inspect.signature(f)
        if "user" in sig.parameters:
            kwargs["user"] = user
        elif "current_user" in sig.parameters:
            kwargs["current_user"] = user
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Flask decorator: requires a valid JWT Bearer token and role in ('admin', 'hod').
    Raises 403 Forbidden if the user is a standard faculty member.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user_from_request()
        if user.role not in ("admin", "hod"):
            raise APIError("Admin access required", 403)
        g.current_user = user
        sig = inspect.signature(f)
        if "admin" in sig.parameters:
            kwargs["admin"] = user
        elif "user" in sig.parameters:
            kwargs["user"] = user
        elif "current_user" in sig.parameters:
            kwargs["current_user"] = user
        return f(*args, **kwargs)
    return decorated


def is_admin_or_hod(user: Faculty) -> bool:
    """Utility to check if a user possesses administrative privileges."""
    return user.role in ("admin", "hod")


def enforce_faculty_privacy(user: Faculty, target_faculty_id: int):
    """
    Enforces that faculty accounts can only access their own data.
    Admin / HOD accounts retain authorized administrative access.
    """
    if user.role == "faculty" and user.id != target_faculty_id:
        raise APIError(
            "Access denied: You are only authorized to access your own faculty data.",
            403
        )
