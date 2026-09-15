"""
utils/auth_utils.py
Small helpers used by auth_routes.py — kept separate so routes stay thin.
"""

import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))


def is_valid_password(password: str) -> bool:
    """Minimum viable password policy: 6+ chars. Tighten later if needed."""
    return bool(password) and len(password) >= 6
