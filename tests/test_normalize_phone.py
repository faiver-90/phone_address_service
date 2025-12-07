import pytest

from app.services.normalize_phone import normalize_phone


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("+7 (999) 123-45-67", "79991234567"),
        ("8 999 123 45 67", "89991234567"),
        (" (099)-123-45-67 ", "0991234567"),
        ("+1-202-555-0182", "12025550182"),
        ("+380 (44) 123 45 67", "380441234567"),
        ("123456", "123456"),
        ("---+++((()))", ""),
        ("+7-999-abc-45-67", "79994567"),
        ("", ""),
        ("   123   ", "123"),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected
