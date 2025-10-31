# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-31

### Added
- Initial release of Image-to-Bookkeeping-Log (itbl)
- Offline OCR processing using Tesseract
- Support for receipts, invoices, checks, and bank statements
- Field extraction: date, amount, vendor, check numbers
- Document classification into P&L categories
- Multiple output formats: CSV, XLSX, Google Sheets
- Triage system for highlighting ambiguous fields
- Deduplication based on content hash and vendor/date/amount
- Image preprocessing: rotation, deskewing, denoising
- Support for JPG, PNG, TIFF, and HEIC image formats
- Configurable vendor mapping and classification rules
- Comprehensive documentation and troubleshooting guides

### Features
- **CLI Commands**: `parse`, `write`, `review`, `run`
- **Output Formats**: CSV, XLSX, Google Sheets with formatting
- **Triage Mode**: Yellow highlighting for low-confidence extractions
- **Auto-detection**: Document type detection (check vs statement vs receipt)
- **Smart Extraction**: Handles OCR errors and multiple transaction formats

### Documentation
- README with setup and usage instructions
- PRD (Product Requirements Document)
- Troubleshooting guides for common issues
- Google Sheets setup guide
- Glossary of technical terms

