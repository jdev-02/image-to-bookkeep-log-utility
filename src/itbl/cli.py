"""CLI entry point."""

import sys
from pathlib import Path
from typing import Optional

from itbl.ingest.loader import find_image_files, load_image
from itbl.ingest.preprocess import preprocess_image
from itbl.normalize.dedupe import Deduplicator
from itbl.normalize.schemas import build_normalized_row
from itbl.normalize.validate import Validator
from itbl.ocr.tesseract import TesseractBackend
from itbl.output.csv_writer import CSVWriter
from itbl.output.gsheet_writer import GoogleSheetsWriter
from itbl.output.xlsx_writer import XLSXWriter
from itbl.parse.classify import Classifier
from itbl.parse.extractors import FieldExtractor
from itbl.parse.categories.checks import extract_check_fields
from itbl.parse.categories.bank_statements import extract_statement_fields
from itbl.review.report import generate_report
from itbl.review.triage import TriageEngine
from itbl.util.config import get_config_dir, load_rules_config, load_sheets_config
from itbl.util.logging import setup_logging

logger = setup_logging()


def parse_command(
    input_path: Path,
    output_path: Path,
    engine: str = "tesseract",
    target: str = "csv",
    triage: bool = False,
    strict_level: str = "medium",
    dry_run: bool = False,
    highlight_color: str = "#FFF59D",
    csv_annotate: bool = False,
    config_dir: Optional[Path] = None,
    no_network: bool = True,
) -> int:
    """
    Parse images and generate normalized output.
    
    Returns:
        Exit code: 0 = success, 2 = staged (needs review), 3 = fatal error
    """
    try:
        if config_dir is None:
            config_dir = get_config_dir()

        # Load configs
        rules_config = load_rules_config(config_dir)
        date_formats = rules_config.get("date_formats", ["%m/%d/%Y", "%Y-%m-%d"])
        currency_symbols = rules_config.get("currency_symbols", ["$", "USD"])

        # Initialize components
        ocr_backend = TesseractBackend() if engine == "tesseract" else None
        if ocr_backend is None:
            logger.error(f"Unknown OCR engine: {engine}")
            return 3

        extractor = FieldExtractor(date_formats=date_formats, currency_symbols=currency_symbols)
        classifier = Classifier(config_dir=str(config_dir) if config_dir else None)
        validator = Validator(strict_level=strict_level)
        triage_engine = TriageEngine(strict_level=strict_level) if triage else None
        deduplicator = Deduplicator()

        # Select writer
        if target == "csv":
            writer = CSVWriter(annotate_inline=csv_annotate)
        elif target == "xlsx":
            writer = XLSXWriter(highlight_color=highlight_color)
        elif target == "google-sheets":
            if no_network:
                logger.error("Google Sheets requires network access (remove --no-network)")
                return 3
            if not sheet_id:
                logger.error("--sheet-id required for Google Sheets")
                return 3
            writer = GoogleSheetsWriter(sheet_id=sheet_id, highlight_color=highlight_color)
        else:
            logger.error(f"Unsupported target: {target}")
            return 3

        # Find images
        image_files = find_image_files(input_path)
        if not image_files:
            logger.warning(f"No images found in {input_path}")
            return 2

        logger.info(f"Found {len(image_files)} image(s)")

        # Process images
        all_rows_by_category = {}  # Group by category for reporting

        for img_path in image_files:
            try:
                logger.info(f"Processing {img_path.name}...")

                # Load and preprocess
                image = load_image(img_path)
                processed = preprocess_image(image)

                # OCR
                ocr_result = ocr_backend.extract(processed)

                # Detect document type (checks/statements vs receipts/invoices)
                # Simple heuristic: check for check keywords
                text_lower = ocr_result.text.lower()
                is_check = any(word in text_lower for word in ["pay to the order", "check", "dollars"])
                is_statement = any(word in text_lower for word in ["statement", "balance", "transaction"])

                # Extract fields
                if is_check:
                    check_data = extract_check_fields(ocr_result.text)
                    extracted = {
                        "date": check_data.get("date"),
                        "vendor": check_data.get("payee"),
                        "amount": check_data.get("amount_digits"),
                        "amount_words": check_data.get("amount_words"),
                        "check_number": check_data.get("check_number"),
                        "memo": check_data.get("memo"),
                        "_ocr_confidence": ocr_result.confidence,
                        "_low_conf_tokens": [t for t in ocr_result.tokens if t.get("confidence", 1.0) < 0.80],
                    }
                elif is_statement:
                    stmt_data = extract_statement_fields(ocr_result.text)
                    extracted = {
                        "date": stmt_data.get("date"),
                        "vendor": stmt_data.get("description"),
                        "amount": stmt_data.get("amount"),
                        "description": stmt_data.get("description"),
                        "_ocr_confidence": ocr_result.confidence,
                        "_low_conf_tokens": [t for t in ocr_result.tokens if t.get("confidence", 1.0) < 0.80],
                    }
                else:
                    # Standard receipt/invoice
                    extracted = extractor.extract_all(ocr_result)

                # Classify
                category, category_conf, hints = classifier.classify(extracted)

                # Build normalized row
                row = build_normalized_row(extracted, str(img_path), category, hints)

                # Validate
                violations = validator.validate_row(row, category)

                # Triage
                if triage_engine:
                    row = triage_engine.analyze_row(row, violations)

                # Check duplicates
                if not deduplicator.is_duplicate(row):
                    if category not in all_rows_by_category:
                        all_rows_by_category[category] = []
                    all_rows_by_category[category].append(row)
                else:
                    logger.info(f"Skipping duplicate: {img_path.name}")

            except Exception as e:
                logger.error(f"Error processing {img_path.name}: {e}", exc_info=True)
                continue

        if dry_run:
            total = sum(len(rows) for rows in all_rows_by_category.values())
            logger.info(f"DRY RUN: Would write {total} rows across {len(all_rows_by_category)} categories")
            for category, rows in list(all_rows_by_category.items())[:3]:
                for row in rows[:2]:  # Show first 2 per category
                    logger.info(f"[{category}] {row.get('Date')} | {row.get('Vendor')} | {row.get('Amount')}")
            return 0

        # Write output by category
        total_rows = 0
        for category, rows in all_rows_by_category.items():
            if not rows:
                continue

            apply_highlights = triage and target in ["xlsx", "google-sheets"]
            writer.write(
                rows,
                output_path,
                category,
                apply_highlights=apply_highlights,
            )
            total_rows += len(rows)
            logger.info(f"Wrote {len(rows)} rows to {category}")

        if total_rows == 0:
            logger.warning("No rows to write")
            return 2

        # Generate report
        generate_report(all_rows_by_category, output_path)

        # Check if any rows were flagged
        has_flags = any(
            any(r.get("_flags") for r in rows)
            for rows in all_rows_by_category.values()
        )

        return 2 if has_flags else 0  # 2 = staged if flags present

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 3


def write_command(
    target: str,
    sheet_id: Optional[str] = None,
    apply_highlights: bool = False,
    input_path: Optional[Path] = None,
) -> int:
    """
    Write staged output to Google Sheets.
    
    Args:
        target: Output target (google-sheets)
        sheet_id: Google Sheets ID
        apply_highlights: Apply yellow highlighting
        input_path: Path to staged CSV/XLSX files (not yet implemented)
    """
    if target != "google-sheets":
        logger.error(f"write command only supports google-sheets, got {target}")
        return 3

    if not sheet_id:
        logger.error("--sheet-id required")
        return 3

    try:
        writer = GoogleSheetsWriter(sheet_id=sheet_id)
        # TODO: Read from staged files and write to Sheets
        logger.warning("write command: reading from staged files not yet implemented")
        logger.info("Use 'itbl parse' with --target google-sheets instead")
        return 3
    except Exception as e:
        logger.error(f"Error writing to Sheets: {e}")
        return 3


def review_command(input_path: Path) -> int:
    """Interactive review of staged items."""
    # TODO: Implement in M3
    logger.error("review command not yet implemented (M3)")
    return 3


def run_command(
    input_path: Path,
    output_path: Path,
    triage: bool = False,
    strict_level: str = "medium",
    target: str = "csv",
    no_network: bool = True,
) -> int:
    """End-to-end run."""
    return parse_command(
        input_path=input_path,
        output_path=output_path,
        target=target,
        triage=triage,
        strict_level=strict_level,
        no_network=no_network,
    )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Image-to-Bookkeeping-Log: Offline image ingestion with triage"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse images and stage output")
    parse_parser.add_argument("input", type=Path, help="Input path (file or directory)")
    parse_parser.add_argument("--out", type=Path, default=Path("./staging"), help="Output path")
    parse_parser.add_argument("--engine", default="tesseract", help="OCR engine (default: tesseract)")
    parse_parser.add_argument("--target", default="csv", choices=["csv", "xlsx", "google-sheets"], help="Output target")
    parse_parser.add_argument("--triage", action="store_true", help="Enable triage mode")
    parse_parser.add_argument("--strict-level", default="medium", choices=["low", "medium", "high"], help="Strictness level")
    parse_parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parse_parser.add_argument("--highlight-color", default="#FFF59D", help="Highlight color (hex)")
    parse_parser.add_argument("--csv-annotate", action="store_true", help="Add inline annotations to CSV")
    parse_parser.add_argument("--config", type=Path, help="Config directory")
    parse_parser.add_argument("--no-network", action="store_true", default=True, help="Enforce offline mode")
    parse_parser.add_argument("--sheet-id", help="Google Sheets ID (required for google-sheets target)")

    # write command
    write_parser = subparsers.add_parser("write", help="Write to Google Sheets")
    write_parser.add_argument("--target", default="google-sheets", help="Target")
    write_parser.add_argument("--sheet-id", required=True, help="Google Sheets ID")
    write_parser.add_argument("--apply-highlights", action="store_true", help="Apply yellow highlights")
    write_parser.add_argument("--input", type=Path, help="Staged input path (not yet implemented)")

    # review command
    review_parser = subparsers.add_parser("review", help="Interactive review")
    review_parser.add_argument("input", type=Path, help="Staged output path")

    # run command
    run_parser = subparsers.add_parser("run", help="End-to-end run")
    run_parser.add_argument("input", type=Path, help="Input path")
    run_parser.add_argument("--out", type=Path, default=Path("./exports"), help="Output path")
    run_parser.add_argument("--triage", action="store_true", help="Enable triage mode")
    run_parser.add_argument("--strict-level", default="medium", choices=["low", "medium", "high"])
    run_parser.add_argument("--target", default="csv", choices=["csv", "xlsx", "google-sheets"])
    run_parser.add_argument("--no-network", action="store_true", default=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "parse":
        return parse_command(
            input_path=args.input,
            output_path=args.out,
            engine=args.engine,
            target=args.target,
            triage=args.triage,
            strict_level=args.strict_level,
            dry_run=args.dry_run,
            highlight_color=args.highlight_color,
            csv_annotate=args.csv_annotate,
            config_dir=args.config,
            no_network=args.no_network,
            sheet_id=getattr(args, "sheet_id", None),
        )
    elif args.command == "write":
        return write_command(
            target=args.target,
            sheet_id=getattr(args, "sheet_id", None),
            apply_highlights=args.apply_highlights,
            input_path=getattr(args, "input", None),
        )
    elif args.command == "review":
        return review_command(args.input)
    elif args.command == "run":
        return run_command(
            input_path=args.input,
            output_path=args.out,
            triage=args.triage,
            strict_level=args.strict_level,
            target=args.target,
            no_network=args.no_network,
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())

