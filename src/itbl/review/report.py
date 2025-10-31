"""Generate review report with triage metrics."""

from pathlib import Path
from typing import Dict, List

from itbl.util.logging import setup_logging

logger = setup_logging()


def generate_report(
    rows_by_category: Dict[str, List[Dict]],
    output_path: Path,
) -> None:
    """
    Generate report.md with triage metrics and recommendations.
    
    Args:
        rows_by_category: Dict mapping category names to lists of rows
        output_path: Path to write report.md
    """
    report_lines = [
        "# Image-to-Bookkeeping-Log Run Report",
        "",
        "## Summary",
        "",
    ]

    total_rows = sum(len(rows) for rows in rows_by_category.values())
    total_flagged = sum(
        len([r for r in rows if r.get("_flags")])
        for rows in rows_by_category.values()
    )

    report_lines.extend([
        f"- Total rows processed: {total_rows}",
        f"- Rows flagged for review: {total_flagged}",
        f"- Flag rate: {total_flagged / total_rows * 100:.1f}%" if total_rows > 0 else "- Flag rate: 0%",
        "",
        "## Triage Metrics by Category",
        "",
    ])

    # Per-category breakdown
    for category, rows in rows_by_category.items():
        if not rows:
            continue

        flagged_count = len([r for r in rows if r.get("_flags")])
        report_lines.extend([
            f"### {category}",
            f"- Total rows: {len(rows)}",
            f"- Flagged rows: {flagged_count}",
            "",
        ])

        # Count flags by field
        field_flags = {}
        reason_counts = {}
        for row in rows:
            flags = row.get("_flags", [])
            highlight_cells = row.get("_highlight_cells", [])

            for flag in flags:
                reason_counts[flag] = reason_counts.get(flag, 0) + 1

            for cell in highlight_cells:
                field_flags[cell] = field_flags.get(cell, 0) + 1

        if field_flags:
            report_lines.append("**Flagged fields:**")
            for field, count in sorted(field_flags.items(), key=lambda x: -x[1]):
                report_lines.append(f"- {field}: {count} cells")

        if reason_counts:
            report_lines.append("**Top reasons:**")
            for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1])[:5]:
                report_lines.append(f"- {reason}: {count}")

        report_lines.append("")

    # Vendor map recommendations
    report_lines.extend([
        "## Vendor Map Recommendations",
        "",
        "Consider adding these vendors to `config/vendors.yaml` to reduce flags:",
        "",
    ])

    # Collect vendors that appear frequently but aren't mapped
    vendor_counts = {}
    for rows in rows_by_category.values():
        for row in rows:
            vendor = row.get("Vendor") or row.get("Vendor/Supplier") or row.get("Vendor/Payee")
            if vendor and row.get("_flags"):
                vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

    top_vendors = sorted(vendor_counts.items(), key=lambda x: -x[1])[:10]
    if top_vendors:
        for vendor, count in top_vendors:
            report_lines.append(f"- `{vendor}` ({count} flagged rows)")
    else:
        report_lines.append("- No vendor recommendations (all mapped or low frequency)")

    report_lines.extend([
        "",
        "## Notes",
        "",
        "- Review flagged cells in output files",
        "- Update vendor map to improve classification accuracy",
        "- Check OCR quality for low-confidence tokens",
        "",
    ])

    # Write report
    report_path = output_path / "report.md" if output_path.is_dir() else output_path.parent / "report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info(f"Report written to {report_path}")

