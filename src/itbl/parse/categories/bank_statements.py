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

    # Extract date (look for dates in various formats)
    date, _ = extract_date(text)
    result["date"] = date

    # Pattern 1: Traditional statement format "Date | Description | Amount"
    transaction_patterns = [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+([A-Za-z0-9\s&.,\-]+?)\s+([\-\+]?\$?\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)",
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

    # Pattern 2: Simple format "VENDOR/LOCATION $amount" (common in credit card statements)
    # This pattern matches: "THE HOME DEPOT 2676 $433.96" or "DUNKIN #331430 $5.55"
    # Also handles: "THE HOME DEPOT #2676 LEOMINSTER MA $115.81"
    # Pattern: Match vendor (may include store #), optionally followed by location "CITY ST", then $amount
    # We match vendor up to a point where we see a location pattern or directly see the $amount
    simple_pattern = r"([A-Z][A-Z0-9\s&#.,/\-]+?)\s+(?:([A-Z][A-Z\s]+\s+[A-Z]{2})\s+)?\$(\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})?)"
    simple_matches = re.finditer(simple_pattern, text)
    for match in simple_matches:
        vendor_desc = match.group(1).strip()
        location = match.group(2)  # Optional location like "LEOMINSTER MA"
        amount_str = match.group(3)
        
        # Clean up vendor name - remove trailing numbers/locations
        vendor_clean = vendor_desc.strip()
        
        # Remove trailing state codes like "MA", "NH", etc.
        vendor_clean = re.sub(r'\s+[A-Z]{2}\s*$', '', vendor_clean)
        
        # Remove trailing store numbers/IDs that appear after vendor name
        # Patterns: "#2676", "2676", "LEOMINSTER MA" at the end
        vendor_clean = re.sub(r'\s+#?\d+\s*$', '', vendor_clean)  # Remove trailing numbers
        vendor_clean = re.sub(r'\s+[A-Z\s]+\s+[A-Z]{2}\s*$', '', vendor_clean)  # Remove "LOCATION MA" pattern
        vendor_clean = vendor_clean.strip()
        
        # Skip if looks like a location instead of vendor (e.g., "LUNENBURG MA")
        words = vendor_clean.split()
        if len(words) <= 2:
            # Check if it's likely a location (all caps, long words typical of city names)
            if any(len(w) >= 6 and w.isupper() for w in words):
                continue
        
        # Skip if vendor name is too short or looks like garbage
        if len(vendor_clean) < 3 or len(vendor_clean) > 80:
            continue
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in vendor_clean):
            continue
        
        try:
            amount = float(amount_str.replace(",", ""))
            if amount > 0:  # Only consider positive amounts (charges)
                transactions.append({
                    "date": None,  # Date not in this format
                    "description": vendor_clean,
                    "amount_str": f"${amount:.2f}",
                    "amount": amount,
                })
        except ValueError:
            continue

    # Process transactions - prefer largest amount (likely most significant transaction)
    if transactions:
        # Sort by amount (descending), prefer ones with dates
        def tx_sort_key(tx):
            tx_amount = tx.get("amount")
            if tx_amount is None:
                try:
                    tx_amount = float(tx["amount_str"].replace("$", "").replace(",", "").strip())
                except (ValueError, KeyError):
                    tx_amount = 0
            has_date = 1 if tx.get("date") else 0
            return (has_date, -tx_amount)  # Prefer dated, then by amount descending
        
        transactions.sort(key=tx_sort_key, reverse=True)
        
        # Log found transactions for debugging
        import logging
        logger = logging.getLogger("itbl")
        logger.debug(f"Statement extractor found {len(transactions)} transactions:")
        for i, tx in enumerate(transactions[:5], 1):  # Log first 5
            logger.debug(f"  {i}. {tx.get('description')} - ${tx.get('amount', 0):.2f}")
        
        tx = transactions[0]
        
        result["date"] = tx.get("date") or result["date"]  # Use extracted date if available
        result["description"] = tx["description"]
        
        # Parse amount
        if "amount" in tx:
            result["amount"] = tx["amount"]
        else:
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

