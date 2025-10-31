"""Classification: vendor map, heuristics, confidence scoring."""

import re
from typing import Dict, List, Optional, Tuple

from itbl.util.config import load_vendors_config


class Classifier:
    """Classifies documents into P&L categories."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize classifier.
        
        Args:
            config_dir: Optional config directory path
        """
        self.vendor_map = load_vendors_config(config_dir) if config_dir else load_vendors_config()
        self.category_keywords = self._build_keyword_map()

    def classify(
        self,
        extracted: Dict,
        sidecar_category: Optional[str] = None,
    ) -> Tuple[str, float, Dict]:
        """
        Classify document into category.
        
        Priority: (1) Sidecar → (2) Vendor map → (3) Heuristics → (4) Unclassified
        
        Args:
            extracted: Dict from FieldExtractor with vendor, date, amount, etc.
            sidecar_category: Optional override from sidecar metadata
        
        Returns:
            Tuple of (category, confidence, hints_dict)
        """
        vendor = extracted.get("vendor", "")

        # Priority 1: Sidecar override
        if sidecar_category:
            return sidecar_category, 1.0, {}

        # Priority 2: Vendor map
        vendor_match = self._match_vendor(vendor)
        if vendor_match:
            category = vendor_match["category"]
            hints = vendor_match.get("hints", {})
            return category, 0.95, hints

        # Priority 3: Keyword heuristics
        heuristics_result = self._classify_by_heuristics(extracted)
        if heuristics_result:
            category, conf = heuristics_result
            return category, conf, {}

        # Priority 4: Unclassified
        return "Unclassified", 0.0, {}

    def _match_vendor(self, vendor: str) -> Optional[Dict]:
        """Match vendor against vendor map."""
        if not vendor:
            return None

        vendor_lower = vendor.lower()

        for entry in self.vendor_map:
            # Exact match
            if "match" in entry:
                match_str = entry["match"].lower()
                if match_str in vendor_lower or vendor_lower in match_str:
                    return entry

            # Regex match
            if "match_regex" in entry:
                pattern = entry["match_regex"]
                try:
                    if re.search(pattern, vendor, re.IGNORECASE):
                        return entry
                except re.error:
                    continue

        return None

    def _classify_by_heuristics(self, extracted: Dict) -> Optional[Tuple[str, float]]:
        """Classify using keyword heuristics."""
        text = str(extracted).lower()
        vendor = (extracted.get("vendor") or "").lower()

        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text or keyword in vendor:
                    score += 1

            if score > 0:
                confidence = min(0.85, 0.60 + (score * 0.10))
                return category, confidence

        return None

    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """Build keyword-to-category mapping."""
        return {
            "Office Supplies": [
                "staples", "office depot", "office max", "paper", "pen", "pencil",
                "folder", "binder", "envelope", "staple", "printer", "ink", "toner"
            ],
            "Marketing": [
                "google ads", "facebook ads", "meta ads", "advertising", "marketing",
                "social media", "campaign", "promotion", "adwords", "x ads"
            ],
            "COGS": [
                "aws", "amazon web services", "azure", "gcp", "cloud", "hosting",
                "server", "infrastructure", "supplier", "inventory", "product"
            ],
            "Insurance": [
                "insurance", "blue cross", "health", "liability", "policy",
                "coverage", "premium", "deductible"
            ],
            "Professional Services": [
                "consulting", "legal", "accountant", "attorney", "lawyer",
                "professional", "service", "advisor"
            ],
            "R&D": [
                "research", "development", "software", "tool", "library", "framework",
                "sdk", "api", "development tool"
            ],
            "Transportation": [
                "mileage", "gas", "fuel", "uber", "lyft", "taxi", "parking",
                "toll", "car", "vehicle", "mile"
            ],
            "Bank Fees": [
                "bank fee", "transaction fee", "service charge", "overdraft",
                "atm fee", "wire fee", "financial"
            ],
            "Revenue": [
                "invoice", "payment received", "revenue", "income", "sale",
                "customer payment"
            ],
        }

