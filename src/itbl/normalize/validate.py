"""Validation rules per category."""

from typing import Dict, List, Optional


class ValidationRule:
    """A validation rule for a field or row."""

    def __init__(self, field: str, rule_type: str, params: Dict | None = None):
        """
        Initialize validation rule.
        
        Args:
            field: Field name to validate
            rule_type: Type of rule (required, date_format, numeric, etc.)
            params: Rule-specific parameters
        """
        self.field = field
        self.rule_type = rule_type
        self.params = params or {}


class Validator:
    """Validates normalized rows per category rules."""

    def __init__(self, strict_level: str = "medium"):
        """
        Initialize validator.
        
        Args:
            strict_level: "low", "medium", or "high"
        """
        self.strict_level = strict_level

    def validate_row(self, row: Dict, category: str) -> List[str]:
        """
        Validate a row and return list of violation reasons.
        
        Args:
            row: Normalized row dict
            category: Category/tab name
        
        Returns:
            List of violation reason codes
        """
        violations = []

        # Common rules
        if category in ["Revenue", "COGS", "Bank Fees"]:
            # Strict on date/amount
            if not row.get("Date"):
                violations.append("parse_error:date_missing")
            if not row.get("Amount") or row.get("Amount") == 0:
                violations.append("parse_error:amount_missing")

        # Check for required fields per category
        required_fields = self._get_required_fields(category)
        for field in required_fields:
            if not row.get(field):
                violations.append(f"rule_violation:required_field_missing:{field}")

        # Check date format (should be YYYY-MM-DD if present)
        if row.get("Date"):
            date_str = str(row["Date"])
            if not date_str.startswith("20") or len(date_str) < 10:
                violations.append("rule_violation:invalid_date_format")

        # Check amount is numeric and positive (unless category allows negatives)
        amount = row.get("Amount")
        if amount is not None:
            try:
                amt_float = float(amount)
                if amt_float < 0 and category not in ["Bank Fees"]:
                    violations.append("rule_violation:negative_amount")
            except (ValueError, TypeError):
                violations.append("parse_error:amount_not_numeric")

        return violations

    def _get_required_fields(self, category: str) -> List[str]:
        """Get required fields for a category."""
        base_required = []
        if category in [
            "Revenue",
            "COGS",
            "R&D",
            "Professional Services",
            "Office Supplies",
            "Marketing",
            "Insurance",
            "Bank Fees",
        ]:
            base_required = ["Date", "Amount"]
        elif category == "Transportation":
            base_required = ["Date"]  # Amount or (Miles AND Rate/Mile)
        return base_required

