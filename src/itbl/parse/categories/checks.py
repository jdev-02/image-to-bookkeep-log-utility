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
    # Handle common OCR errors: "1Q" -> "TO", "0" -> "O", etc.
    payee_patterns = [
        r"PAY\s+(?:TO|1Q|T0)\s+THE\s+ORDER\s+OF[:\s]+([A-Za-z0-9\s&.,\-'']+?)(?:\s+CUSTOMER|\s+DETAILS|\s+NON|\s+COPY|$)",  # Stop at common check text
        r"PAY\s+(?:TO|1Q|T0)[:\s]+([A-Za-z0-9\s&.,\-'']+?)(?:\s+CUSTOMER|\s+DETAILS|\s+COPY|$)",
        r"PAYEE[:\s]+([A-Za-z0-9\s&.,\-'']+)",
    ]
    for pattern in payee_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            payee = match.group(1).strip()
            # Clean up common OCR artifacts
            payee = re.sub(r'\s+', ' ', payee)  # Multiple spaces to single
            if len(payee) > 3:  # Must be substantial
                result["payee"] = payee
                break

    # Extract amount in digits (usually after $ or in amount box)
    amount_patterns = [
        r"\$\s*(\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",  # Standard $123.45
        r"(\d{1,3}(?:[,.]\d{3})*\.\d{2})\s*(?:dollars?|DOLLARS?)",  # 123.45 DOLLARS
        r"\$\s*(\d+)\.?(\d{0,2})",  # $123 or $123.45 (flexible)
        r"AMOUNT[:\s]+\$?\s*(\d+(?:\.\d{2})?)",  # "AMOUNT: $123.45"
        r"(\d{1,5}(?:\.\d{2})?)\s*$",  # Amount at end of line (common in check amount box)
    ]
    candidates = []
    for pattern in amount_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            try:
                if len(match.groups()) == 2:
                    # Handle pattern with optional cents
                    dollars = match.group(1)
                    cents = match.group(2) if match.group(2) else "00"
                    amount_str = f"{dollars}.{cents.zfill(2)}"
                else:
                    amount_str = match.group(1)
                amount_str = amount_str.replace(",", "")
                amount = float(amount_str)
                if amount > 0 and amount < 1000000:  # Reasonable check range
                    candidates.append((amount, len(match.group(0))))  # Store with length for preference
            except (ValueError, IndexError):
                continue
    
    # Pick the largest reasonable amount (usually the check amount)
    if candidates:
        # Sort by amount descending, then by match length (longer matches are more specific)
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        result["amount_digits"] = candidates[0][0]

    # Extract amount in words (for cross-check)
    words_patterns = [
        r"(\w+(?:\s+\w+)*)\s+Dollars?",
        r"(\w+(?:\s+\w+)*)\s+DOLLARS?",
    ]
    for pattern in words_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["amount_words"] = match.group(1).strip()

    # Extract check number (can be at start of text, with or without dashes)
    check_num_patterns = [
        r"CHECK\s*#?\s*(\d+(?:[-\s]\d+)*)",
        r"CHECK\s+NUMBER[:\s]+(\d+(?:[-\s]\d+)*)",
        r"#\s*(\d{3,}(?:[-\s]\d+)*)",  # Common check number format
        r"^(\d{2,}[-\s]\d{3,})",  # At start: "52-0133" or "52 0133"
        r"^(\d{4,})",  # At start: plain number 4+ digits
    ]
    for pattern in check_num_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            check_num = match.group(1).strip().replace(' ', '')  # Remove spaces
            if len(check_num.replace('-', '')) >= 4:  # At least 4 digits
                result["check_number"] = check_num
                break

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

