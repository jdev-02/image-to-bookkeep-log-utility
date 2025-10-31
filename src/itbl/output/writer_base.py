"""Base writer interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class WriterBase(ABC):
    """Base class for output writers."""

    @abstractmethod
    def write(
        self,
        rows: List[Dict],
        output_path: Path,
        category: str,
        apply_highlights: bool = False,
    ) -> None:
        """
        Write rows to output.
        
        Args:
            rows: List of normalized row dicts
            output_path: Output file/directory path
            category: Category/tab name
            apply_highlights: Whether to apply yellow highlighting
        """
        pass

