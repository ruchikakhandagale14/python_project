import re

def is_valid_email(email: str) -> bool:
    return bool(email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def is_valid_name(name: str) -> bool:
    """Name must be at least 2 characters and contain only letters, spaces or dots."""
    return bool(name and re.fullmatch(r"[A-Za-z][A-Za-z .]{1,99}", name.strip()))

def is_valid_mobile(mobile: str) -> bool:
    return bool(mobile and re.fullmatch(r"\d{10}", mobile))

def is_valid_percentage(value: float) -> bool:
    return 0 <= value <= 100

def is_valid_backlog_count(value: int) -> bool:
    return value >= 0
