"""Extractor for check documents."""

import re
from typing import Dict, Optional, Tuple

from itbl.parse.common import extract_date


def extract_check_fields(text: str) -> Dict:
    """
    Extract fields from a check image.
    
    Args:
        text: OCR text from check
    
    Returns:
        Dict with: date, payee, amount_digits, amount_words, check_number, memo
    """
    result = {
        "date": None,
        "payee": None,
        "amount_digits": None,
        "amount_words": None,
        "check_number": None,
        "memo": None,
        "_check_amount_conflict": False,
    }

    # Extract date (usually top-right on check)
    date, _ = extract_date(text)
    result["date"] = date

    # Extract payee (usually "PAY TO THE ORDER OF")
    payee_patterns = [
        r"PAY\s+TO\s+THE\s+ORDER\s+OF[:\s]+([A-Za-z0-9\s&.,\-]+)",
        r"PAY\s+TO[:\s]+([A-Za-z0-9\s&.,\-]+)",
        r"PAYEE[:\s]+([A-Za-z0-9\s&.,\-]+)",
    ]
    for pattern in payee_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            result["payee"] = match.group(1).strip()
            break

    # Extract amount in digits (usually after $)
    amount_patterns = [
        r"\$\s*(\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
        r"(\d{1,3}(?:[,.]\d{3})*\.\d{2})\s*(?:dollars?|DOLLARS?)",
    ]
    for pattern in amount_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount_str = match.group(1).replace(",", "")
                amount = float(amount_str)
                result["amount_digits"] = amount
                break
            except ValueError:
                continue

    # Extract amount in words (for cross-check)
    words_patterns = [
        r"(\w+(?:\s+\w+)*)\s+Dollars?",
        r"(\w+(?:\s+\w+)*)\s+DOLLARS?",
    ]
    for pattern in words_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["amount_words"] = match.group(1).strip()

    # Extract check number
    check_num_patterns = [
        r"CHECK\s*#?\s*(\d+)",
        r"CHECK\s+NUMBER[:\s]+(\d+)",
        r"#\s*(\d{4,})",  # Common check number format
    ]
    for pattern in check_num_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["check_number"] = match.group(1)

    # Extract memo
    memo_patterns = [
        r"MEMO[:\s]+(.+)",
        r"FOR[:\s]+(.+)",
    ]
    for pattern in memo_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            result["memo"] = match.group(1).strip()[:100]  # Limit length
            break

    # Cross-check amount (digits vs words)
    if result["amount_digits"] and result["amount_words"]:
        # Basic validation: words should match digits (simplified)
        # Full implementation would convert words to number
        pass  # TODO: Add word-to-number conversion for full validation

    return result


def words_to_number(words: str) -> Optional[float]:
    """
    Convert written amount to number (simplified).
    
    Example: "One Hundred Twenty Three and 45/100" -> 123.45
    
    This is a placeholder - full implementation would handle all number words.
    """
    # TODO: Implement full word-to-number conversion
    # For now, return None to indicate it needs manual verification
    return None

