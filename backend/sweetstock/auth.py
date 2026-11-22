"""Authentication validation and password handling."""

import hmac
import re
import sqlite3
from typing import Any

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash


ALLOWED_ROLES = {"customer", "employee"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration(payload: Any) -> str | None:
    """Return a client-facing validation message, or None when valid."""
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"

    required_fields = ("name", "email", "phone", "password", "role")
    if any(not isinstance(payload.get(field), str) or not payload[field].strip() for field in required_fields):
        return "name, email, phone, password, and role are required"
    if not EMAIL_PATTERN.match(payload["email"].strip()):
        return "Enter a valid email address"
    if len(payload["password"]) < 6:
        return "Password must be at least 6 characters"
    if payload["role"] not in ALLOWED_ROLES:
        return "Account role must be customer or employee"
    return None


def validate_login(payload: Any) -> str | None:
    """Return a client-facing validation message, or None when valid."""
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    if (
        not isinstance(payload.get("email"), str)
        or not isinstance(payload.get("password"), str)
        or not payload["email"].strip()
        or not payload["password"]
    ):
        return "Email and password are required"
    return None


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a database user row to a safe API response."""
    return {
        "user_id": row["user_id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "role": row["role"],
        "created": row["created"],
    }


def password_matches(stored_password: str, supplied_password: str) -> bool:
    """Check hashed passwords and support one-time migration of seed passwords."""
    if not stored_password.startswith(("scrypt:", "pbkdf2:", "argon2:")):
        return hmac.compare_digest(stored_password, supplied_password)
    return check_password_hash(stored_password, supplied_password)


def hash_password(password: str) -> str:
    """Create a password hash suitable for database storage."""
    return generate_password_hash(password)


def set_authenticated_user(user_id: int) -> None:
    """Store the authenticated user ID in the signed Flask session."""
    session.clear()
    session["user_id"] = user_id


def clear_authenticated_user() -> None:
    """Remove the authenticated user from the current session."""
    session.clear()
