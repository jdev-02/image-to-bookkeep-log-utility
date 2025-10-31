"""Structured logging with PII redaction."""

import logging
import re
from typing import Any

# PAN regex: 13-19 digits, possibly with spaces/dashes
PAN_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4,7}\b")

# SSN pattern
SSN_PATTERN = re.compile(r"\b\d{3}[\s-]?\d{2}[\s-]?\d{4}\b")

# Email pattern (basic)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def redact_pii(text: str) -> str:
    """Redact PAN, SSN, and email from log messages."""
    text = PAN_PATTERN.sub("[PAN]", text)
    text = SSN_PATTERN.sub("[SSN]", text)
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    return text


class PIIFilter(logging.Filter):
    """Log filter that redacts PII."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and redact PII from log records."""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = redact_pii(record.msg)
        if hasattr(record, "args") and record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    new_args.append(redact_pii(arg))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        return True


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Set up structured logging with PII redaction."""
    logger = logging.getLogger("itbl")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(PIIFilter())
        logger.addHandler(handler)

    return logger

