from datetime import datetime
import re
from decimal import Decimal, InvalidOperation


CONCEPT_RE = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s\-\.,:/()&'+]+$")


def parse_year_month(value, fallback):
    try:
        return datetime.strptime(value, "%Y-%m")
    except Exception:
        return fallback


def validate_concept(value):
    concept = (value or "").strip()
    if not concept:
        return None, "Concept is required."
    if not CONCEPT_RE.fullmatch(concept):
        return None, "Concept contains invalid characters. Allowed: letters, numbers, spaces and . , - / ( ) : & ' +"
    return concept, None


def validate_amount(value):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, "Amount must be a valid number."
    if amount <= 0:
        return None, "Amount must be greater than 0."
    return amount, None
