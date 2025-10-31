"""CSV writer with triage column support."""

import csv
from pathlib import Path
from typing import Dict, List

from itbl.output.writer_base import WriterBase


class CSVWriter(WriterBase):
    """CSV writer with triage annotations."""

    def __init__(self, annotate_inline: bool = False, triage_column: str = "_triage"):
        """
        Initialize CSV writer.
        
        Args:
            annotate_inline: If True, wrap flagged values with <<REVIEW: reason>> value
            triage_column: Name of triage column
        """
        self.annotate_inline = annotate_inline
        self.triage_column = triage_column

    def write(
        self,
        rows: List[Dict],
        output_path: Path,
        category: str,
        apply_highlights: bool = False,
    ) -> None:
        """
        Write rows to CSV file.
        
        Args:
            rows: List of normalized row dicts
            output_path: Output file path (or directory; will create category_name.csv)
            category: Category/tab name
            apply_highlights: Ignored for CSV (use triage column instead)
        """
        if output_path.is_dir():
            output_file = output_path / f"{category.replace(' ', '_')}.csv"
        else:
            output_file = output_path

        if not rows:
            return

        # Determine columns (skip hidden fields except _triage)
        hidden_prefixes = ["_"]
        sample_row = rows[0]
        all_cols = set(sample_row.keys())
        visible_cols = [
            col
            for col in all_cols
            if not any(col.startswith(prefix) for prefix in hidden_prefixes)
            or col == self.triage_column
        ]

        # Always include triage column if any row has flags
        has_triage = any(row.get("_flags") for row in rows)
        if has_triage and self.triage_column not in visible_cols:
            visible_cols.append(self.triage_column)

        # Sort columns: put triage last, otherwise maintain order
        if self.triage_column in visible_cols:
            visible_cols.remove(self.triage_column)
            visible_cols.append(self.triage_column)

        # Write CSV
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=visible_cols, extrasaction="ignore")
            writer.writeheader()

            for row in rows:
                out_row = {}
                flags = row.get("_flags", [])
                highlight_cells = row.get("_highlight_cells", [])

                # Build triage info
                triage_info = []
                if flags:
                    triage_info.extend(flags)
                if highlight_cells:
                    triage_info.extend([f"highlight:{cell}" for cell in highlight_cells])

                for col in visible_cols:
                    if col == self.triage_column:
                        out_row[col] = "; ".join(triage_info) if triage_info else ""
                    else:
                        value = row.get(col, "")
                        # Apply inline annotation if flagged
                        if (
                            self.annotate_inline
                            and col in highlight_cells
                            and flags
                        ):
                            reason = flags[0] if flags else "review"
                            out_row[col] = f"<<REVIEW: {reason}>> {value}"
                        else:
                            out_row[col] = value

                writer.writerow(out_row)

