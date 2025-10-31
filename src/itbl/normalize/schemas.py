"""Schema definitions for P&L tabs."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from itbl.util.config import load_sheets_config


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
    # Common fields
    field_mapping = {
        "Date": extracted.get("date"),
        "Amount": extracted.get("amount") or extracted.get("amount_digits"),
        "Vendor": extracted.get("vendor") or extracted.get("payee"),
        "Vendor/Supplier": extracted.get("vendor") or extracted.get("payee"),
        "Vendor/Payee": extracted.get("vendor") or extracted.get("payee"),
        "Vendor/Provider": extracted.get("vendor") or extracted.get("payee"),
        "Vendor/Platform": extracted.get("vendor") or extracted.get("payee"),
        "Payment Method": extracted.get("payment_method") or hints.get("payment_method", ""),
        "Description": extracted.get("description") or "Receipt",
        "Item/Description": extracted.get("description") or "Receipt",
        "Service/Description": extracted.get("description") or "Receipt",
        "Campaign/Description": extracted.get("description") or "Receipt",
        "Business Purpose": extracted.get("business_purpose") or "",
        "Invoice #": extracted.get("invoice_number") or "",
        "Customer/Source": extracted.get("customer") or "",
    }

    # Category-specific mappings
    if category == "Transportation":
        row["Miles"] = extracted.get("miles")
        row["Rate/Mile"] = extracted.get("rate_per_mile")
        row["From"] = extracted.get("from_location") or ""
        row["To"] = extracted.get("to_location") or ""
    elif category == "Insurance":
        row["Insurance Company"] = extracted.get("vendor") or extracted.get("insurance_company", "")
        row["Policy Type"] = extracted.get("policy_type") or hints.get("policy_type", "")
        row["Coverage Period"] = extracted.get("coverage_period") or ""
    elif category == "Bank Fees":
        row["Financial Institution"] = extracted.get("vendor") or extracted.get("financial_institution", "")
        row["Fee Type"] = extracted.get("fee_type") or ""
        row["Account"] = extracted.get("account") or ""
    elif category == "Marketing":
        row["Marketing Type"] = extracted.get("marketing_type") or hints.get("marketing_type", "")
    elif category == "COGS":
        row["Product Line"] = extracted.get("product_line") or hints.get("product_line", "")

    # Apply common mappings
    for col in columns:
        if col in field_mapping and col not in row:
            row[col] = field_mapping[col]
        elif col not in row:
            row[col] = ""  # Empty for unmapped columns

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

