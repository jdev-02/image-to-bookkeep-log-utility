"""Common parsing utilities and patterns."""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from dateutil import parser as date_parser


def extract_date(text: str, date_formats: List[str] | None = None) -> Tuple[Optional[str], float]:
    """
    Extract date from text.
    
    Args:
        text: Input text
        date_formats: Optional list of strftime formats to try
    
    Returns:
        Tuple of (normalized_date_str YYYY-MM-DD, confidence)
    """
    if date_formats is None:
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

    # Try explicit formats first
    for fmt in date_formats:
        pattern = _strftime_to_regex(fmt)
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                dt = datetime.strptime(match.group(0), fmt)
                return dt.strftime("%Y-%m-%d"), 0.95
            except ValueError:
                continue

    # Fallback to dateutil (flexible parsing)
    try:
        # Look for date-like patterns
        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",  # YYYY-MM-DD
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",  # Mon DD, YYYY
        ]
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    dt = date_parser.parse(match.group(0), fuzzy=False)
                    return dt.strftime("%Y-%m-%d"), 0.90
                except (ValueError, TypeError):
                    continue
    except Exception:
        pass

    return None, 0.0


def _strftime_to_regex(fmt: str) -> str:
    """Convert strftime format to regex pattern (simplified)."""
    # Common replacements
    replacements = {
        "%m": r"\d{1,2}",
        "%d": r"\d{1,2}",
        "%Y": r"\d{4}",
        "%y": r"\d{2}",
        "%b": r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
    }
    pattern = fmt
    for old, new in replacements.items():
        pattern = pattern.replace(old, new)
    # Escape other special chars
    pattern = re.escape(pattern)
    # Unescape our patterns
    for old, new in replacements.items():
        escaped_old = re.escape(old)
        if escaped_old in pattern:
            pattern = pattern.replace(escaped_old, new)
    return pattern


def extract_amount(text: str, currency_symbols: List[str] | None = None) -> Tuple[Optional[float], float]:
    """
    Extract monetary amount from text.
    
    Args:
        text: Input text
        currency_symbols: List of currency symbols (default: ["$", "USD"])
    
    Returns:
        Tuple of (amount_float, confidence)
    """
    if currency_symbols is None:
        currency_symbols = ["$", "USD"]

    # Patterns for amounts
    # Look for: $123.45, 123.45, Total: $123.45, Amount Due: 123.45
    patterns = [
        # Currency symbol + number
        r"(?:{})\s*(\d{{1,3}}(?:[,.]\d{{3}})*(?:\.\d{{2}})?)".format(
            "|".join(re.escape(s) for s in currency_symbols)
        ),
        # Number at end of line (common for totals)
        r"(\d{{1,3}}(?:[,.]\d{{3}})*\.\d{{2}})\s*(?:{})?\s*$".format(
            "|".join(re.escape(s) for s in currency_symbols)
        ),
        # Common labels
        r"(?:Total|Amount|Due|Subtotal|Grand Total)[:\s]+\s*(?:{})?\s*(\d{{1,3}}(?:[,.]\d{{3}})*\.\d{{2}})".format(
            "|".join(re.escape(s) for s in currency_symbols)
        ),
    ]

    candidates = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            amount_str = match.group(1).replace(",", "")
            try:
                amount = float(amount_str)
                if amount > 0:
                    candidates.append((amount, 0.95))
            except ValueError:
                continue

    if not candidates:
        return None, 0.0

    # Return the largest amount (likely the total)
    best = max(candidates, key=lambda x: x[0])
    return best[0], best[1]


def extract_vendor(text: str) -> Tuple[Optional[str], float]:
    """
    Extract vendor/payee name from text.
    
    Args:
        text: Input text
    
    Returns:
        Tuple of (vendor_name, confidence)
    """
    # Look for company names at the beginning of lines
    # Common patterns: COMPANY NAME, Inc., LLC, Corp, etc.
    lines = text.split("\n")
    if not lines:
        return None, 0.0

    # First substantial line often contains vendor
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 3 and len(line) < 100:
            # Check for common business suffixes
            if re.search(
                r"\b(?:Inc|LLC|Corp|Ltd|Co|Company|LLP)\b", line, re.IGNORECASE
            ):
                return line, 0.85
            # Otherwise, take first substantial line
            if len(line) > 10:
                return line, 0.70

    # Fallback: return first non-empty line
    for line in lines:
        line = line.strip()
        if len(line) > 5:
            return line, 0.60

    return None, 0.0

