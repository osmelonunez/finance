from datetime import datetime
import pytest

from i18n import format_money, format_number
from validators import parse_year_month, validate_amount, validate_concept, validate_text_length


pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value,lang,expected",
    [
        (1234.56, "es", "1.234,56"),
        (1234.56, "en", "1,234.56"),
        (1234567, "es", "1.234.567,00"),
        (1234567, "en", "1,234,567.00"),
    ],
)
def test_format_money_groups_digits(value, lang, expected):
    assert format_money(value, lang) == expected


def test_format_number_groups_digits():
    assert format_number(1234567, "es") == "1.234.567"
    assert format_number(1234567, "en") == "1,234,567"


@pytest.mark.parametrize("value", ["10", "10.50", "0.01"])
def test_validate_amount_accepts_positive_values(value):
    amount, error = validate_amount(value)
    assert amount > 0
    assert error is None


@pytest.mark.parametrize("value", ["", "0", "-1", "not-a-number"])
def test_validate_amount_rejects_invalid_values(value):
    amount, error = validate_amount(value)
    assert amount is None
    assert error


def test_validate_concept_and_length_limits():
    assert validate_concept("Valid concept")[1] is None
    assert validate_concept("")[1]
    assert validate_concept("x" * 41)[1]
    assert validate_concept("Invalid @ concept")[1]
    assert validate_text_length("x" * 501, "Comment", 500)[1]


def test_parse_year_month_uses_fallback_for_invalid_value():
    fallback = datetime(2026, 1, 1)
    assert parse_year_month("2026-07", fallback) == datetime(2026, 7, 1)
    assert parse_year_month("invalid", fallback) is fallback
