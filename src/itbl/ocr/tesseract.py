"""Tesseract OCR backend implementation."""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pytesseract
from PIL import Image

from itbl.ocr.base import OCRBackend, OCRResult


def find_tesseract_executable() -> str | None:
    """Try to find Tesseract executable on Windows if not in PATH."""
    import platform
    
    if platform.system() != "Windows":
        return None
    
    # Common Windows installation locations
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return None


class TesseractBackend(OCRBackend):
    """Tesseract OCR backend."""

    def __init__(
        self,
        dpi: int = 300,
        psm: int = 6,  # Assume uniform block of text
        oem: int = 3,  # Default OCR engine mode
        lang: str = "eng",
        tesseract_cmd: str | None = None,
    ):
        """
        Initialize Tesseract backend.
        
        Args:
            dpi: Image DPI assumption
            psm: Page segmentation mode (6 = uniform block)
            oem: OCR engine mode (3 = default)
            lang: Language code (e.g., 'eng')
            tesseract_cmd: Path to tesseract.exe (auto-detected if None)
        """
        self.dpi = dpi
        self.psm = psm
        self.oem = oem
        self.lang = lang
        
        # Try to find Tesseract if not in PATH
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Check if we need to set the path
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                # Not in PATH, try to find it
                found_path = find_tesseract_executable()
                if found_path:
                    pytesseract.pytesseract.tesseract_cmd = found_path
                    import logging
                    logging.getLogger("itbl").info(f"Auto-detected Tesseract at: {found_path}")

    def extract(self, image: Image.Image, **kwargs) -> OCRResult:
        """
        Extract text using Tesseract.
        
        Args:
            image: PIL Image
            **kwargs: Override dpi, psm, oem, lang if provided
        
        Returns:
            OCRResult
        """
        dpi = kwargs.get("dpi", self.dpi)
        psm = kwargs.get("psm", self.psm)
        oem = kwargs.get("oem", self.oem)
        lang = kwargs.get("lang", self.lang)

        config = f"--dpi {dpi} --psm {psm} --oem {oem} -l {lang}"

        # Get detailed data with confidence
        data = pytesseract.image_to_data(
            image, config=config, output_type=pytesseract.Output.DICT
        )

        # Extract full text
        text = pytesseract.image_to_string(image, config=config).strip()

        # Build tokens with confidence
        tokens = []
        words = data["text"]
        confidences = data["conf"]
        for word, conf in zip(words, confidences):
            if word.strip():  # Skip empty
                conf_float = float(conf) / 100.0 if conf != "-1" else 0.0
                tokens.append(
                    {
                        "text": word,
                        "confidence": conf_float,
                        "left": data["left"][words.index(word)],
                        "top": data["top"][words.index(word)],
                        "width": data["width"][words.index(word)],
                        "height": data["height"][words.index(word)],
                    }
                )

        # Compute overall confidence (average of valid tokens)
        valid_confs = [
            float(c) / 100.0 for c in confidences if c != "-1" and c != "0"
        ]
        overall_conf = sum(valid_confs) / len(valid_confs) if valid_confs else 0.0

        return OCRResult(
            text=text,
            confidence=overall_conf,
            tokens=tokens,
            layout={"mode": "tesseract", "config": config},
        )

    def get_confidence_per_token(self, result: OCRResult) -> List[Tuple[str, float]]:
        """Extract (token, confidence) pairs from OCRResult."""
        return [(token["text"], token["confidence"]) for token in result.tokens]

