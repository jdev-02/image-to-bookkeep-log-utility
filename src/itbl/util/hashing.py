"""Content hashing utilities for deduplication."""

import hashlib
from pathlib import Path
from typing import Dict, Any


def hash_file(file_path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_content(content: bytes) -> str:
    """Compute SHA256 hash of content bytes."""
    return hashlib.sha256(content).hexdigest()


def compute_row_hash(row: Dict[str, Any]) -> str:
    """Compute hash for deduplication based on vendor, date, amount."""
    # Create a stable string representation
    vendor = str(row.get("_vendor") or row.get("Vendor") or "").lower().strip()
    date = str(row.get("Date") or "").strip()
    amount = str(row.get("Amount") or 0).strip()

    content = f"{vendor}|{date}|{amount}".encode("utf-8")
    return hashlib.md5(content).hexdigest()  # MD5 is sufficient for dedupe

