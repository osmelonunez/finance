import re


_PATTERNS = [
    # postgresql://user:password@host/db
    re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://[^:\s/]+:)([^@\s]+)(@)"),
    # password=..., token: ..., secret: ...
    re.compile(r"(?i)\b(password|passwd|pwd|token|secret|smtp_password|database_url)\b(\s*[:=]\s*)([^\s,;]+)"),
    # JSON-like "password": "..."
    re.compile(r'(?i)"(password|passwd|pwd|token|secret|smtp_password|database_url)"\s*:\s*"([^"]+)"'),
    # Python-like 'password': '...'
    re.compile(r"(?i)'(password|passwd|pwd|token|secret|smtp_password|database_url)'\s*:\s*'([^']+)'"),
]


def redact_text(text: str) -> str:
    if not text:
        return text
    redacted = text
    redacted = _PATTERNS[0].sub(r"\1***\3", redacted)
    redacted = _PATTERNS[1].sub(r"\1\2***", redacted)
    redacted = _PATTERNS[2].sub(r'"\1":"***"', redacted)
    redacted = _PATTERNS[3].sub(r"'\1':'***'", redacted)
    return redacted

