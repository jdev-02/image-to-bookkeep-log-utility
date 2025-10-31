"""Extractor for bank statement documents."""

import re
from typing import Dict, Optional

from itbl.parse.common import extract_date


def extract_statement_fields(text: str) -> Dict:
    """
    Extract fields from a bank statement.
    
    Args:
        text: OCR text from statement
    
    Returns:
        Dict with: date, description, amount, balance, transaction_type
    """
    result = {
        "date": None,
        "description": None,
        "amount": None,
        "balance": None,
        "transaction_type": None,  # "debit", "credit", "unknown"
    }

    # Extract date
    date, _ = extract_date(text)
    result["date"] = date

    # Find transaction lines
    # Common patterns: Date | Description | Amount | Balance
    transaction_patterns = [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+([A-Za-z0-9\s&.,\-]+?)\s+([\-\+]?\$?\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+([A-Za-z0-9\s&.,\-]+?)\s+([\-\+]?\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
    ]

    transactions = []
    for pattern in transaction_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            transactions.append({
                "date": match.group(1),
                "description": match.group(2).strip(),
                "amount_str": match.group(3),
            })

    # Process first substantial transaction (skip headers)
    if transactions:
        tx = transactions[0]  # Or iterate through all
        result["date"] = tx["date"]
        result["description"] = tx["description"]

        # Parse amount and determine type
        amount_str = tx["amount_str"].replace("$", "").replace(",", "").strip()
        if amount_str.startswith("-") or amount_str.startswith("+"):
            sign = amount_str[0]
            amount_str = amount_str[1:]
            result["transaction_type"] = "debit" if sign == "-" else "credit"
        else:
            # Try to infer from context
            desc_lower = tx["description"].lower()
            if any(word in desc_lower for word in ["withdrawal", "debit", "payment", "charge"]):
                result["transaction_type"] = "debit"
            elif any(word in desc_lower for word in ["deposit", "credit", "payment received"]):
                result["transaction_type"] = "credit"

        try:
            amount = float(amount_str)
            if result["transaction_type"] == "debit":
                amount = -abs(amount)  # Ensure negative for debits
            result["amount"] = amount
        except ValueError:
            pass

    # Extract balance if present
    balance_patterns = [
        r"BALANCE[:\s]+\$?(\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
        r"ENDING\s+BALANCE[:\s]+\$?(\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
    ]
    for pattern in balance_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result["balance"] = float(match.group(1).replace(",", ""))
                break
            except ValueError:
                continue

    return result

