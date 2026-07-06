import logging
import os

from log_safety import redact_text


RESET = "\033[0m"
LEVEL_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[1;31m",
}


def color_enabled(log_format="text"):
    raw = (os.environ.get("LOG_COLOR") or "auto").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return log_format != "json"


class RedactingTextFormatter(logging.Formatter):
    def format(self, record):
        return redact_text(super().format(record))


class ColorRedactingTextFormatter(RedactingTextFormatter):
    def format(self, record):
        line = super().format(record)
        color = LEVEL_COLORS.get(record.levelname)
        if not color:
            return line
        return f"{color}{line}{RESET}"


def text_formatter(fmt, use_color=True):
    formatter_class = ColorRedactingTextFormatter if use_color else RedactingTextFormatter
    return formatter_class(fmt)
