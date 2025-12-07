import re


def normalize_phone(phone: str) -> str:
    """
    Accepts a phone number in any format and returns a string containing only digits.
    Removes spaces, parentheses, dashes, plus signs, and decimalization.
    """
    digits = re.sub(r"\D+", "", phone)

    return digits
