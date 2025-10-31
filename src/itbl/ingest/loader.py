"""File loader for images and PDFs."""

import io
from pathlib import Path
from typing import Iterator, List

from PIL import Image


# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".heif"}
PDF_EXTENSIONS = {".pdf"}


def find_image_files(path: Path, recursive: bool = True) -> List[Path]:
    """Find all supported image files in a path."""
    files = []
    if path.is_file():
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(path)
    elif path.is_dir():
        pattern = "**/*" if recursive else "*"
        for ext in IMAGE_EXTENSIONS:
            files.extend(path.glob(f"{pattern}{ext}"))
            files.extend(path.glob(f"{pattern}{ext.upper()}"))
    return sorted(files)


def find_pdf_files(path: Path, recursive: bool = True) -> List[Path]:
    """Find all PDF files in a path."""
    files = []
    if path.is_file():
        if path.suffix.lower() in PDF_EXTENSIONS:
            files.append(path)
    elif path.is_dir():
        pattern = "**/*" if recursive else "*"
        files.extend(path.glob(f"{pattern}.pdf"))
        files.extend(path.glob(f"{pattern}.PDF"))
    return sorted(files)


def load_image(file_path: Path) -> Image.Image:
    """Load an image file."""
    try:
        return Image.open(file_path)
    except Exception as e:
        raise IOError(f"Failed to load image {file_path}: {e}") from e


def split_pdf_pages(pdf_path: Path) -> Iterator[Image.Image]:
    """
    Split a PDF into page images.
    
    Note: This is a placeholder. Full PDF support would require pdf2image or similar.
    For now, we skip PDFs and document that they require additional dependencies.
    """
    # TODO: Implement with pdf2image when needed
    raise NotImplementedError(
        "PDF support requires pdf2image. Install: pip install pdf2image"
    )

