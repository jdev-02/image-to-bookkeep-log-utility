"""Triage system for ambiguity detection and highlighting."""

from typing import Dict, List

from itbl.util.config import load_rules_config


class TriageEngine:
    """Detects ambiguities and flags cells for review."""

    def __init__(self, strict_level: str = "medium", ocr_conf_threshold: float = 0.80):
        """
        Initialize triage engine.
        
        Args:
            strict_level: "low", "medium", or "high"
            ocr_conf_threshold: Minimum OCR confidence (default 0.80)
        """
        self.strict_level = strict_level
        self.ocr_conf_threshold = ocr_conf_threshold
        
        # Load config for thresholds
        rules_config = load_rules_config()
        triage_config = rules_config.get("triage", {})
        self.ocr_conf_threshold = triage_config.get("ocr_conf_threshold", ocr_conf_threshold)
        self.amount_delta_pct = triage_config.get("amount_delta_pct", 0.05)
        self.reasons = triage_config.get("reasons", [
            "low_conf", "multi_candidates", "parse_error",
            "rule_violation", "category_conflict", "incomplete"
        ])

    def analyze_row(self, row: Dict, validation_violations: List[str] = None) -> Dict:
        """
        Analyze a row for ambiguities and compute flags/highlights.
        
        Args:
            row: Normalized row dict
            validation_violations: List of validation violation codes
        
        Returns:
            Updated row dict with _flags and _highlight_cells
        """
        flags = []
        highlight_cells = []
        validation_violations = validation_violations or []

        # Check OCR confidence
        ocr_conf = row.get("_ocr_confidence", 1.0)
        if ocr_conf < self.ocr_conf_threshold:
            flags.append("low_conf")
            # Highlight fields with low confidence tokens
            low_conf_fields = self._get_low_conf_fields(row)
            highlight_cells.extend(low_conf_fields)

        # Check field-level confidences
        date_conf = row.get("_date_confidence", 1.0)
        amount_conf = row.get("_amount_confidence", 1.0)
        vendor_conf = row.get("_vendor_confidence", 1.0)

        if date_conf < self.ocr_conf_threshold and row.get("Date"):
            flags.append("low_conf:date")
            highlight_cells.append("Date")
        elif not row.get("Date"):
            flags.append("parse_error:date")
            highlight_cells.append("Date")

        if amount_conf < self.ocr_conf_threshold and row.get("Amount"):
            flags.append("low_conf:amount")
            highlight_cells.append("Amount")
        elif not row.get("Amount"):
            flags.append("parse_error:amount")
            highlight_cells.append("Amount")

        if vendor_conf < self.ocr_conf_threshold and row.get("Vendor"):
            flags.append("low_conf:vendor")
            highlight_cells.append("Vendor")
        elif not row.get("Vendor"):
            flags.append("parse_error:vendor")
            highlight_cells.append("Vendor")

        # Check validation violations
        for violation in validation_violations:
            if violation.startswith("parse_error:"):
                flags.append(violation)
                field = violation.split(":")[-1]
                if field not in highlight_cells:
                    highlight_cells.append(field)
            elif violation.startswith("rule_violation:"):
                flags.append(violation)
                # Extract field from violation if possible
                parts = violation.split(":")
                if len(parts) > 2:
                    field = parts[-1]
                    if field not in highlight_cells:
                        highlight_cells.append(field)

        # Update row
        row["_flags"] = list(set(flags))  # Deduplicate
        row["_highlight_cells"] = list(set(highlight_cells))  # Deduplicate

        return row

    def _get_low_conf_fields(self, row: Dict) -> List[str]:
        """Get field names that have low confidence tokens."""
        low_conf_tokens = row.get("_low_conf_tokens", [])
        if not low_conf_tokens:
            return []

        # Map tokens to likely fields (simplified)
        # In a full implementation, we'd track which tokens map to which fields
        fields = []
        text_content = str(row).lower()
        if any("date" in text_content or "vendor" in text_content for _ in low_conf_tokens):
            # Conservative: flag common fields if any low conf tokens
            if row.get("Date"):
                fields.append("Date")
            if row.get("Vendor"):
                fields.append("Vendor")
            if row.get("Amount"):
                fields.append("Amount")
        return fields

