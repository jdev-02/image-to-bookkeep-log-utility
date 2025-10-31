"""Base OCR backend interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from PIL import Image


class OCRResult:
    """OCR result container."""

    def __init__(
        self,
        text: str,
        confidence: float,
        tokens: List[Dict[str, Any]] | None = None,
        layout: Dict | None = None,
    ):
        """
        Initialize OCR result.
        
        Args:
            text: Full extracted text
            confidence: Overall confidence (0.0-1.0)
            tokens: List of token-level results with confidence
            layout: Layout information (blocks, lines, words)
        """
        self.text = text
        self.confidence = confidence
        self.tokens = tokens or []
        self.layout = layout or {}


class OCRBackend(ABC):
    """Base class for OCR backends."""

    @abstractmethod
    def extract(self, image: Image.Image, **kwargs) -> OCRResult:
        """
        Extract text from image.
        
        Args:
            image: Preprocessed PIL Image
            **kwargs: Backend-specific options
        
        Returns:
            OCRResult with text, confidence, and tokens
        """
        pass

    @abstractmethod
    def get_confidence_per_token(self, result: OCRResult) -> List[Tuple[str, float]]:
        """
        Get confidence per token.
        
        Args:
            result: OCRResult from extract()
        
        Returns:
            List of (token, confidence) tuples
        """
        pass

