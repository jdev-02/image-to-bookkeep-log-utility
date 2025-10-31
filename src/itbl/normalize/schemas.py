"""Schema definitions for P&L tabs."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from itbl.util.config import load_sheets_config


def _get_missing_field_explanation(
    field_name: str,
    extracted: Dict,
    flags: List[str] = None,
) -> str:
    """
    Generate explanatory text for missing fields.
    
    Args:
        field_name: Name of the field (e.g., "Date", "Vendor", "Amount")
        extracted: Extracted data dict
        flags: List of triage flags (optional, may be added later)
    
    Returns:
        Explanatory string for why field is missing
    """
    flags = flags or []
    field_lower = field_name.lower()
    flags_str = " ".join(flags) if flags else ""
    
    # Check if field was attempted but failed to parse
    if f"parse_error:{field_lower}" in flags_str:
        return "Could not parse from image - manual review needed"
    
    # Check confidence levels
    conf_key = f"_{field_lower}_confidence"
    confidence = extracted.get(conf_key, 1.0)
    
    if confidence > 0 and confidence < 0.50:
        return "Low confidence extraction - needs manual review"
    elif f"low_conf:{field_lower}" in flags_str:
        return "Low confidence - extracted but may be inaccurate"
    
    # Check OCR confidence
    ocr_conf = extracted.get("_ocr_confidence", 1.0)
    if ocr_conf < 0.50:
        return "OCR quality too low - field not in image or unreadable"
    
    # Default: field simply not found/not provided in image
    return "Not supplied in image"


def update_row_with_explanations(row: Dict) -> Dict:
    """
    Update row with explanatory text for missing fields based on flags.
    Call this after triage has run and flags are available.
    
    Args:
        row: Row dict with flags and extracted data
    
    Returns:
        Updated row with explanations in place of empty/missing fields
    """
    flags = row.get("_flags", [])
    extracted = {
        "date": row.get("Date"),
        "amount": row.get("Amount"),
        "vendor": row.get("Vendor") or row.get("Vendor/Supplier") or row.get("Vendor/Payee") or row.get("Vendor/Provider") or row.get("Vendor/Platform"),
        "_date_confidence": row.get("_date_confidence", 1.0),
        "_amount_confidence": row.get("_amount_confidence", 1.0),
        "_vendor_confidence": row.get("_vendor_confidence", 1.0),
        "_ocr_confidence": row.get("_ocr_confidence", 1.0),
    }
    
    # Update Date if missing or is explanation placeholder
    if not row.get("Date") or row.get("Date") == "Not supplied in image":
        row["Date"] = _get_missing_field_explanation("Date", extracted, flags)
    
    # Update Amount if missing or is explanation placeholder
    if not row.get("Amount") or (isinstance(row.get("Amount"), str) and "supplied" in row.get("Amount", "").lower()):
        # Only replace if it's actually an explanation string, not a number
        if not isinstance(row.get("Amount"), (int, float)):
            row["Amount"] = _get_missing_field_explanation("Amount", extracted, flags)
    
    # Update Vendor variants if missing
    vendor_fields = ["Vendor", "Vendor/Supplier", "Vendor/Payee", "Vendor/Provider", "Vendor/Platform", "Insurance Company", "Financial Institution"]
    for field in vendor_fields:
        if field in row and (not row[field] or row[field] == "Not supplied in image"):
            row[field] = _get_missing_field_explanation("Vendor", extracted, flags)
    
    # Update other common fields
    other_fields = {
        "Payment Method": "Payment Method",
        "Business Purpose": "Business Purpose",
        "Invoice #": "Invoice",
        "Customer/Source": "Customer",
    }
    for field, field_key in other_fields.items():
        if field in row and (not row[field] or row[field] == "Not supplied in image"):
            # For optional fields, just use default explanation
            if not row[field]:
                row[field] = "Not supplied in image"
    
    return row


def build_normalized_row(
    extracted: Dict,
    source_file: str,
    category: str,
    hints: Dict | None = None,
) -> Dict:
    """
    Build a normalized row for any category tab.
    
    Args:
        extracted: Dict from FieldExtractor or category-specific extractor
        source_file: Source image path
        category: Category/tab name
        hints: Optional hints from vendor map or classification
    
    Returns:
        Normalized row dict with tab columns
    """
    hints = hints or {}
    sheets_config = load_sheets_config()
    columns = sheets_config["tabs"].get(category, [])

    row = {
        "_row_id": str(uuid.uuid4()),
        "_source_file": source_file,
        "_category": category,
        "_created_at": datetime.now().isoformat(),
        "_flags": [],
        "_highlight_cells": [],
    }

    # Map extracted fields to schema columns
    # Common fields - use explanatory text only if truly missing
    date_val = extracted.get("date")
    amount_val = extracted.get("amount") or extracted.get("amount_digits")
    vendor_val = extracted.get("vendor") or extracted.get("payee")
    
    field_mapping = {
        "Date": date_val if date_val else "Not supplied in image",
        "Amount": amount_val if amount_val is not None else "Not supplied in image",
        "Vendor": vendor_val if vendor_val else "Not supplied in image",
        "Vendor/Supplier": vendor_val if vendor_val else "Not supplied in image",
        "Vendor/Payee": vendor_val if vendor_val else "Not supplied in image",
        "Vendor/Provider": vendor_val if vendor_val else "Not supplied in image",
        "Vendor/Platform": vendor_val if vendor_val else "Not supplied in image",
        "Payment Method": extracted.get("payment_method") or hints.get("payment_method") or "Not supplied in image",
        "Description": extracted.get("description") or "Receipt",
        "Item/Description": extracted.get("description") or "Receipt",
        "Service/Description": extracted.get("description") or "Receipt",
        "Campaign/Description": extracted.get("description") or "Receipt",
        "Business Purpose": extracted.get("business_purpose") or "Not supplied in image",
        "Invoice #": extracted.get("invoice_number") or "Not supplied in image",
        "Customer/Source": extracted.get("customer") or "Not supplied in image",
    }

    # Category-specific mappings - use explanatory text if missing
    if category == "Transportation":
        row["Miles"] = extracted.get("miles") or "Not supplied in image"
        row["Rate/Mile"] = extracted.get("rate_per_mile") or "Not supplied in image"
        row["From"] = extracted.get("from_location") or "Not supplied in image"
        row["To"] = extracted.get("to_location") or "Not supplied in image"
    elif category == "Insurance":
        row["Insurance Company"] = (extracted.get("vendor") or extracted.get("insurance_company")) or "Not supplied in image"
        row["Policy Type"] = extracted.get("policy_type") or hints.get("policy_type") or "Not supplied in image"
        row["Coverage Period"] = extracted.get("coverage_period") or "Not supplied in image"
    elif category == "Bank Fees":
        row["Financial Institution"] = (extracted.get("vendor") or extracted.get("financial_institution")) or "Not supplied in image"
        row["Fee Type"] = extracted.get("fee_type") or "Not supplied in image"
        row["Account"] = extracted.get("account") or "Not supplied in image"
    elif category == "Marketing":
        row["Marketing Type"] = extracted.get("marketing_type") or hints.get("marketing_type") or "Not supplied in image"
    elif category == "COGS":
        row["Product Line"] = extracted.get("product_line") or hints.get("product_line") or "Not supplied in image"

    # Apply common mappings
    for col in columns:
        if col in field_mapping and col not in row:
            row[col] = field_mapping[col]
        elif col not in row:
            row[col] = "Not supplied in image"  # Explanatory text for unmapped columns

    # Copy confidence fields
    row["_date_confidence"] = extracted.get("_date_confidence", 0.0)
    row["_amount_confidence"] = extracted.get("_amount_confidence", 0.0)
    row["_vendor_confidence"] = extracted.get("_vendor_confidence", 0.0)
    row["_ocr_confidence"] = extracted.get("_ocr_confidence", 0.0)
    row["_low_conf_tokens"] = extracted.get("_low_conf_tokens", [])

    return row


def build_office_supplies_row(
    extracted: Dict,
    source_file: str,
    category: str = "Office Supplies",
) -> Dict:
    """Build a normalized row for Office Supplies tab (backward compatibility)."""
    return build_normalized_row(extracted, source_file, category)


def get_all_tab_schemas() -> Dict[str, List[str]]:
    """Get all tab column schemas from config."""
    sheets_config = load_sheets_config()
    return sheets_config.get("tabs", {})

