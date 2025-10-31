"""Field extractors for receipts, invoices, etc."""

from typing import Dict, Optional

from itbl.ocr.base import OCRResult
from itbl.parse.common import extract_amount, extract_date, extract_vendor


class FieldExtractor:
    """Extracts common fields from OCR text."""

    def __init__(
        self,
        date_formats: list[str] | None = None,
        currency_symbols: list[str] | None = None,
    ):
        """
        Initialize extractor.
        
        Args:
            date_formats: Date format strings to try
            currency_symbols: Currency symbols to recognize
        """
        self.date_formats = date_formats
        self.currency_symbols = currency_symbols

    def extract_all(self, ocr_result: OCRResult) -> Dict[str, any]:
        """
        Extract all common fields from OCR result.
        
        Args:
            ocr_result: OCRResult from OCR backend
        
        Returns:
            Dict with fields: date, amount, vendor, and their confidences
        """
        text = ocr_result.text

        # Extract fields
        date, date_conf = extract_date(text, self.date_formats)
        amount, amount_conf = extract_amount(text, self.currency_symbols)
        vendor, vendor_conf = extract_vendor(text)

        # Check OCR token confidence for flagged fields
        low_conf_tokens = [
            token for token in ocr_result.tokens if token.get("confidence", 1.0) < 0.80
        ]

        result = {
            "date": date,
            "amount": amount,
            "vendor": vendor,
            "_date_confidence": date_conf,
            "_amount_confidence": amount_conf,
            "_vendor_confidence": vendor_conf,
            "_ocr_confidence": ocr_result.confidence,
            "_low_conf_tokens": low_conf_tokens,
        }

        return result

