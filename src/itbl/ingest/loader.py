"""File loader for images and PDFs."""

import io
from pathlib import Path
from typing import Iterator, List

from PIL import Image

# Try to register HEIC support if pillow-heif is available
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


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
    
    # Deduplicate (important on Windows where filesystem is case-insensitive)
    # Convert to absolute paths and use a set to remove duplicates
    seen = set()
    unique_files = []
    for f in files:
        abs_path = f.resolve()
        if abs_path not in seen:
            seen.add(abs_path)
            unique_files.append(f)
    
    return sorted(unique_files)


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
    
    # Deduplicate (important on Windows where filesystem is case-insensitive)
    seen = set()
    unique_files = []
    for f in files:
        abs_path = f.resolve()
        if abs_path not in seen:
            seen.add(abs_path)
            unique_files.append(f)
    
    return sorted(unique_files)


def load_image(file_path: Path) -> Image.Image:
    """
    Load an image file.
    
    Supports: JPG, PNG, TIFF, HEIC (if pillow-heif is installed)
    """
    # Check for HEIC/HEIF files and provide helpful error if not supported
    if file_path.suffix.lower() in {".heic", ".heif"}:
        if not HEIC_SUPPORTED:
            raise IOError(
                f"HEIC/HEIF format not supported. "
                f"Please install pillow-heif: pip install pillow-heif\n"
                f"Or convert {file_path.name} to JPG/PNG format first."
            )
    
    try:
        return Image.open(file_path)
    except Exception as e:
        # Provide more helpful error for HEIC files
        if file_path.suffix.lower() in {".heic", ".heif"}:
            raise IOError(
                f"Failed to load HEIC image {file_path}: {e}\n"
                f"If pillow-heif is installed, this may be a file corruption issue.\n"
                f"Try converting the file to JPG/PNG format."
            ) from e
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

