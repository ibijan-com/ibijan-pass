"""
Input validation functions for SPG.

All functions return True if valid, False otherwise.
Used by the UI for real-time keystroke validation.
"""

from .config import ALLOWED_SPECIAL_CHARS


def validate_prefix(text: str) -> bool:
    if text == "":
        return True
    return text.isalpha()


def validate_base_number(text: str) -> bool:
    if text == "":
        return True
    return text.isdigit()


def validate_special_chars(text: str) -> bool:
    if text == "":
        return True
    return all(char in ALLOWED_SPECIAL_CHARS for char in text)


def validate_service_name(text: str) -> bool:
    if text == "":
        return True
    return all(char.isalnum() or char in '-_' for char in text)


def validate_profile_name(text: str) -> bool:
    if text == "":
        return True
    return all(char.isalnum() or char in ' _-' for char in text)


def validate_capitalize_letter(text: str) -> bool:
    if text == "":
        return True
    return len(text) == 1 and text.isalpha()
