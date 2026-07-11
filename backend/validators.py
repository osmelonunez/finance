from datetime import datetime
import re
from decimal import Decimal, InvalidOperation


CONCEPT_RE = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s\-\.,:/()&'+]+$")

MAX_RECORD_CONCEPT_LENGTH = 40
MAX_RECORD_COMMENT_LENGTH = 500
MAX_CATEGORY_NAME_LENGTH = 40
MAX_CATEGORY_DESCRIPTION_LENGTH = 500
MAX_PAYMENT_METHOD_NAME_LENGTH = 40
MAX_BANK_NAME_LENGTH = 40
MAX_LOAN_NAME_LENGTH = 40
MAX_LOAN_DESCRIPTION_LENGTH = 500
MAX_LOAN_USAGE_CONCEPT_LENGTH = 40
MAX_LOAN_USAGE_COMMENT_LENGTH = 500


def parse_year_month(value, fallback):
    try:
        return datetime.strptime(value, "%Y-%m")
    except Exception:
        return fallback


def validate_text_length(value, field_name, max_length, required=False):
    text = (value or "").strip()
    if required and not text:
        return None, f"{field_name} is required."
    if text and len(text) > max_length:
        return None, f"{field_name} must be {max_length} characters or fewer."
    return text or None, None


def validate_concept(value, max_length=MAX_RECORD_CONCEPT_LENGTH, field_name="Concept"):
    concept = (value or "").strip()
    if not concept:
        return None, f"{field_name} is required."
    if len(concept) > max_length:
        return None, f"{field_name} must be {max_length} characters or fewer."
    if not CONCEPT_RE.fullmatch(concept):
        return None, f"{field_name} contains invalid characters. Allowed: letters, numbers, spaces and . , - / ( ) : & ' +"
    return concept, None


def validate_amount(value):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, "Amount must be a valid number."
    if amount <= 0:
        return None, "Amount must be greater than 0."
    return amount, None
