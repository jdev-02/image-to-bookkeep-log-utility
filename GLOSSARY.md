# Glossary of Terms and Acronyms

This glossary defines technical terms and acronyms used throughout the image-to-bookkeeping-log project documentation and codebase.

## A

**ACH** - Automated Clearing House. A network for electronic payments and money transfers. In this tool, ACH refers to a payment method type (e.g., direct bank transfers).

**AMEX** - American Express. A credit card company/payment method.

**API** - Application Programming Interface. A set of protocols and tools for building software. In this tool, Google Sheets API allows the tool to read and write to Google Sheets.

## C

**Chocolatey (choco)** - A Windows package manager (like an app store for command-line tools). Not required for this project - you can install Tesseract directly instead.

**CI** - Continuous Integration. A software development practice where code changes are automatically tested and integrated. The project includes CI configuration for automated testing.

**CLI** - Command Line Interface. A text-based way to interact with software by typing commands in a terminal. The `itbl` command is the CLI for this tool.

**COGS** - Cost of Goods Sold. A financial term for the direct costs of producing goods or services. One of the P&L (Profit & Loss) categories this tool organizes expenses into.

**CSV** - Comma-Separated Values. A simple file format that stores tabular data (like spreadsheets) using commas to separate values. This tool can output data as CSV files.

## D

**DPI** - Dots Per Inch. A measure of image resolution or print quality. Higher DPI generally means better image quality for OCR (Optical Character Recognition).

## G

**Google Sheets** - Google's web-based spreadsheet application, similar to Microsoft Excel. This tool can write data directly to Google Sheets spreadsheets.

## H

**HEIC** - High Efficiency Image Container. A modern image format used by Apple devices (iPhone, iPad). This tool supports reading HEIC image files.

## J

**JSON** - JavaScript Object Notation. A lightweight data format used for storing and exchanging data. This tool uses JSON for configuration files and credentials.

**JPG/JPEG** - Joint Photographic Experts Group. A common image file format for photos. This tool supports reading JPG/JPEG files for receipt scanning.

## L

**LLM** - Large Language Model. An AI system trained on vast amounts of text data. This tool does NOT use LLMs or cloud AI services (it's fully offline for privacy).

## O

**OCR** - Optical Character Recognition. Technology that converts images of text (like scanned receipts) into machine-readable text. This tool uses Tesseract OCR to extract text from receipt images offline.

**OEM** - OCR Engine Mode. A setting in Tesseract OCR that controls which OCR algorithm to use. The default mode (3) is the standard OCR engine.

**Offline** - Operating without an internet connection. This tool performs all OCR and text extraction offline for privacy and security, only connecting to the internet when writing to Google Sheets (if you choose that option).

## P

**P&L** - Profit & Loss (Statement). A financial document that shows a company's revenues and expenses over a period. This tool organizes extracted data into P&L categories like Revenue, COGS, Marketing, etc.

**PAN** - Primary Account Number. The number printed on credit/debit cards (typically 13-19 digits). This tool automatically redacts PANs from logs to protect your privacy.

**PDF** - Portable Document Format. A file format for documents that preserves formatting. This tool has placeholder support for PDF files (requires additional software to be installed).

**PII** - Personally Identifiable Information. Data that can identify a specific person (like Social Security Numbers, credit card numbers, email addresses). This tool automatically redacts PII from log files for security.

**PNG** - Portable Network Graphics. An image file format that supports transparency. This tool supports reading PNG image files.

**PSM** - Page Segmentation Mode. A setting in Tesseract OCR that tells the software how to interpret the layout of text on a page. Mode 6 assumes a uniform block of text, which works well for receipts.

**PyTorch** - A machine learning framework. Some optional OCR backends (like docTR) can use PyTorch, but the default Tesseract backend doesn't require it.

## R

**R&D** - Research & Development. Business expenses related to developing new products or services. One of the P&L categories this tool organizes expenses into.

## S

**SDK** - Software Development Kit. A collection of tools and libraries for building software. This tool can integrate with OCR SDKs like PaddleOCR or docTR (optional, not required).

**SSN** - Social Security Number. A 9-digit number used in the United States for tax and identification purposes. This tool automatically redacts SSNs from logs to protect your privacy.

## T

**TIFF** - Tagged Image File Format. A flexible image file format often used for high-quality images. This tool supports reading TIFF image files.

**Tesseract** - An open-source OCR (Optical Character Recognition) engine. This is the default OCR software used by this tool to extract text from images. It runs entirely on your computer (offline).

**Triage** - A process of prioritizing or flagging items that need review. In this tool, "triage mode" automatically highlights cells in yellow that may contain uncertain or ambiguous data, making it easy to spot items that need manual verification.

## U

**UI** - User Interface. The visual elements users interact with (buttons, menus, etc.). This tool uses a CLI (Command Line Interface) rather than a graphical UI.

**UUID** - Universally Unique Identifier. A unique identifier assigned to each row of data processed by the tool. Used internally for tracking and deduplication.

**UX** - User Experience. How users feel when interacting with software. This tool is designed for a straightforward command-line experience.

## V

**VISA** - A credit card company/payment method. This tool recognizes Visa as a payment method type.

## W

**Winget** - Windows Package Manager. A built-in package manager for Windows 10/11. You can use `winget install --id UB-Mannheim.TesseractOCR` to install Tesseract without needing Chocolatey.

## X

**XLSX** - Microsoft Excel format. The modern file format used by Microsoft Excel spreadsheets. This tool can output data as XLSX files with yellow highlighting for cells that need review.

## Y

**YAML** - YAML Ain't Markup Language (a recursive acronym). A human-readable data format often used for configuration files. This tool uses YAML files (`vendors.yaml`, `rules.yaml`, `sheets.yaml`) for configuration.

