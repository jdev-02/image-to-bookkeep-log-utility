# Test Images Directory

Place your test images here (receipts, invoices, checks, bank statements, etc.).

## Supported Formats
- JPG/JPEG
- PNG
- TIFF
- HEIC (Apple format)

## Usage Examples

### Process a single image file:
```bash
itbl parse ./examples/inbox/my_receipt.jpg --out ./staging --target csv
```

### Process all images in this directory:
```bash
itbl parse ./examples/inbox --out ./staging --target csv --triage
```

### Process and send to Google Sheets:
```bash
itbl parse ./examples/inbox --target google-sheets --sheet-id YOUR_SHEET_ID --triage --apply-highlights
```

## Tips
- Name your files descriptively (e.g., `receipt_office_supplies_2024.jpg`)
- You can organize images in subfolders - the tool will find them recursively
- For best OCR results, use clear, well-lit images

