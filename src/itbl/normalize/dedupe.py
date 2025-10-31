"""Deduplication logic."""

from typing import Dict, List, Set

from itbl.util.hashing import compute_row_hash


class Deduplicator:
    """Handles row deduplication."""

    def __init__(self):
        """Initialize deduplicator."""
        self.seen_hashes: Set[str] = set()

    def is_duplicate(self, row: Dict) -> bool:
        """
        Check if row is duplicate.
        
        Args:
            row: Normalized row dict
        
        Returns:
            True if duplicate
        """
        row_hash = compute_row_hash(row)
        if row_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(row_hash)
        return False

    def filter_duplicates(self, rows: List[Dict]) -> List[Dict]:
        """
        Filter duplicate rows from list.
        
        Args:
            rows: List of normalized rows
        
        Returns:
            List with duplicates removed
        """
        unique_rows = []
        for row in rows:
            if not self.is_duplicate(row):
                unique_rows.append(row)
        return unique_rows

