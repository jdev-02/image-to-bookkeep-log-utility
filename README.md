# Image-to-Bookkeeping-Log (itbl)

**A tool that automatically extracts data from receipt images and organizes them into your bookkeeping system.**

This tool scans images of receipts, invoices, checks, and bank statements (using **OCR** - Optical Character Recognition), extracts important information like dates, amounts, and vendors, and organizes everything into **P&L** (Profit & Loss) categories for your business accounting. Everything runs **offline** on your computer for privacy - no images are sent to the cloud.

## Features

- **Offline OCR** (Optical Character Recognition): Fully offline processing using Tesseract (privacy-first). OCR is the technology that reads text from images - all processing happens on your computer, not in the cloud.
- **Multi-format output**: Export to **CSV** (Comma-Separated Values), **XLSX** (Microsoft Excel format), and Google Sheets (Google's web-based spreadsheet)
- **Triage workflow**: Automatic yellow highlighting of ambiguous cells for manual review. Cells that the system is uncertain about are marked in yellow so you can quickly spot items that need verification.
- **Deduplication**: Prevents duplicate entries if you accidentally process the same receipt twice
- **Extensible**: Pluggable OCR backends (Tesseract default, with support for optional alternatives like PaddleOCR/docTR)

## Installation

### Prerequisites

1. **Python 3.11+** (a programming language - download from [python.org](https://www.python.org/downloads/))
2. **Tesseract OCR** (Optical Character Recognition software that reads text from images):
   - **Windows** (choose one option):
     - **Option A - Direct Download** (recommended if Chocolatey is not installed):
       1. Go to [UB Mannheim Tesseract Releases](https://github.com/UB-Mannheim/tesseract/wiki)
       2. Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)
       3. Run the installer and follow the prompts
       4. **Important**: During installation, check "Add to PATH" or manually add Tesseract to your system PATH
       5. After installation, verify by opening a new terminal/PowerShell and running: `tesseract --version`
     - **Option B - Using Chocolatey** (if you have Chocolatey installed):
       - Run: `choco install tesseract`
     - **Option C - Using Winget** (Windows Package Manager, available on Windows 10/11):
       - Run: `winget install --id UB-Mannheim.TesseractOCR`
   - **macOS**: `brew install tesseract` (requires Homebrew)
   - **Linux**: `apt-get install tesseract-ocr` (Debian/Ubuntu) or `yum install tesseract` (Red Hat/CentOS)

### Setup

```bash
# Clone repository (or navigate to the folder if you already have it)
cd image-to-bookkeep-log

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt  # (if created) or from pyproject.toml
```

**Troubleshooting Windows Installation:**

If Tesseract is not found after installation:

1. **Verify Tesseract is installed**: Open PowerShell or Command Prompt and run:
   ```powershell
   tesseract --version
   ```
   If you see an error, Tesseract is not in your PATH.

2. **Add Tesseract to PATH manually**:
   - Find where Tesseract was installed (usually `C:\Program Files\Tesseract-OCR` or `C:\Users\YourUsername\AppData\Local\Programs\Tesseract-OCR`)
   - Copy the full path
   - Right-click "This PC" → Properties → Advanced system settings → Environment Variables
   - Under "System variables" or "User variables", find and select "Path" → Edit
   - Click "New" and paste the Tesseract installation path
   - Click OK on all dialogs
   - **Close and reopen** your terminal/PowerShell for changes to take effect

3. **Alternative**: You can also install Tesseract without adding to PATH, then specify its location:
   ```powershell
   # Set environment variable for this session (PowerShell)
   $env:TESSDATA_PREFIX = "C:\Program Files\Tesseract-OCR\tessdata"
   ```
   Or set the path in your Python code by modifying the Tesseract path in `src/itbl/ocr/tesseract.py` if needed.

### Google Sheets (Optional)

For Google Sheets output (writing directly to Google's online spreadsheets), you'll need:

1. Create a Google Cloud Project (a free Google account project for accessing Google services)
2. Enable Google Sheets API (Application Programming Interface - allows the tool to access Google Sheets)
3. Create OAuth 2.0 credentials (a secure way for the tool to access your Google account)
4. Download `credentials.json` to `~/.config/itbl/` (or set `GOOGLE_APPLICATION_CREDENTIALS`)

See [Google Sheets Setup](#google-sheets-setup) below.

## Quick Start

### Basic Usage

```bash
# Parse images and output CSV (local, offline - no internet needed)
# CSV = Comma-Separated Values, a simple spreadsheet file format
itbl parse ./inbox --out ./staging --target csv

# With triage mode (highlights ambiguous cells in yellow)
# XLSX = Microsoft Excel file format
itbl parse ./inbox --triage --target xlsx --out ./staging

# Preview without writing (see what would be extracted without creating files)
itbl parse ./inbox --dry-run

# End-to-end with triage (complete workflow with yellow highlighting)
itbl run ./inbox --triage --target csv --out ./exports
```

### Command Options

#### `parse` command

```bash
itbl parse <input> [OPTIONS]

Options:
  --out PATH              Output directory (default: ./staging)
  --engine ENGINE        OCR engine: tesseract (default) - the software that reads text from images
  --target FORMAT        Output format: csv (simple text spreadsheet), xlsx (Excel file), google-sheets (online spreadsheet)
  --triage               Enable triage mode (yellow highlighting for uncertain data)
  --strict-level LEVEL   Strictness: low (fewer flags), medium (default), high (more flags for review)
  --dry-run              Preview without writing (see what would be extracted)
  --highlight-color HEX  Highlight color (default: #FFF59D - yellow)
  --csv-annotate         Add inline annotations to CSV (wrap uncertain values with review notes)
  --config PATH          Config directory override
  --no-network           Enforce offline mode (default: true - no internet required)
```

#### `run` command (end-to-end)

```bash
itbl run <input> [OPTIONS]

Options:
  --out PATH              Output directory (default: ./exports)
  --triage                Enable triage mode
  --strict-level LEVEL    Strictness level
  --target FORMAT         Output format
  --no-network            Enforce offline mode
```

## Configuration

Configuration files are in `config/` (all use **YAML** format - a human-readable configuration file format):

- **`sheets.yaml`**: Defines the structure of your spreadsheet tabs and which columns each category should have
- **`rules.yaml`**: Validation rules, triage thresholds (when to flag uncertain data), date formats to recognize
- **`vendors.yaml`**: Maps vendor names (like "Amazon Web Services") to P&L categories (like "COGS" - Cost of Goods Sold)

### Example vendor mapping

```yaml
- match: "Amazon Web Services"
  category: "COGS"  # COGS = Cost of Goods Sold (business expense category)
  hints:
    product_line: "Cloud"
    payment_method: "ACH"  # ACH = Automated Clearing House (bank transfer payment method)

- match_regex: "(?i)google ads|meta ads"
  category: "Marketing"
  hints:
    marketing_type: "Paid Ads"
```

## Output Formats

### CSV (Comma-Separated Values)
A simple text file format that can be opened in Excel, Google Sheets, or any spreadsheet program.

- Adds `_triage` column listing flagged fields (fields that need review)
- Optional inline annotations: `<<REVIEW: reason>> value` (with `--csv-annotate` flag)
- Works offline - no internet connection needed

### XLSX (Microsoft Excel Format)
The standard Excel file format (.xlsx files).

- Yellow-highlighted cells (#FFF59D - a light yellow color) for ambiguous fields
- Cell comments with reason codes (why the field was flagged) and confidence scores (how certain the system is)

### Google Sheets
Google's web-based spreadsheet (requires internet connection).

- Batch-append rows (adds all new rows at once for efficiency)
- Apply yellow background to flagged cells
- Add cell notes with reasons (requires `--apply-highlights` flag)

## Triage System

**Triage** means identifying items that need review. The system automatically flags uncertain data in yellow so you can quickly spot what needs manual verification.

Cells are highlighted yellow when:

- **OCR confidence < 0.80**: The text-reading software (OCR) wasn't very confident about what it read (less than 80% sure)
- **Multiple candidates within 5%**: There are two or more possible values that are very close (like $100.00 vs $100.05)
- **Parse failures**: The system couldn't recognize a date or number format
- **Validation rule violations**: The data doesn't match expected patterns (like a negative amount where it shouldn't be negative)
- **Category conflicts**: The vendor mapping and automatic classification disagree on which category this belongs to
- **Incomplete complementary fields**: Related fields are missing (like having miles but no rate for transportation expenses)

**Reason codes** (shown in cell comments/notes):
- `low_conf`: Low confidence in the extracted value
- `multi_candidates`: Multiple possible values detected
- `parse_error`: Could not parse/recognize the value
- `rule_violation`: Violates a validation rule
- `category_conflict`: Category classification is uncertain
- `incomplete`: Missing related/complementary information

## Google Sheets Setup

For detailed step-by-step instructions with screenshots and troubleshooting, see [docs/GOOGLE_SHEETS_SETUP.md](docs/GOOGLE_SHEETS_SETUP.md).

Quick setup:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (this is free and gives you access to Google's APIs)

2. **Enable APIs** (Application Programming Interfaces - how the tool talks to Google):
   - Enable "Google Sheets API" (allows the tool to read/write to your Google Sheets)
   - Enable "Google Drive API" (if needed for file access)

3. **Configure OAuth Consent Screen**:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (unless you have a Google Workspace, then use "Internal")
   - Fill in required fields:
     - App name: "Image-to-Bookkeeping-Log" (or any name you prefer)
     - User support email: Your email
     - Developer contact email: Your email
   - Click "Save and Continue"
   - For Scopes: Click "Add or Remove Scopes", search for and add:
     - `https://www.googleapis.com/auth/spreadsheets` (Google Sheets API)
   - Click "Save and Continue"
   - For Test users: **IMPORTANT** - Click "ADD USERS" and add your own Google account email address (the one you'll sign in with)
   - Click "Save and Continue" through the remaining screens

4. **Create Credentials** (secure login tokens):
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: Choose "Desktop app"
   - Name: "Image-to-Bookkeeping-Log Client" (or any name)
   - Click "Create"
   - Click "Download JSON" - this downloads your credentials file
   - Save it as `credentials.json`

5. **Place credentials** on your computer:
   - **Windows**: `C:\Users\YourUsername\.config\itbl\credentials.json`
   - **macOS/Linux**: `~/.config/itbl/credentials.json`
   - Or place `credentials.json` in your current working directory
   - Or use `--credentials` flag to specify the path
   - Or set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

6. **First run**:
   - Run `itbl parse ./inbox --target google-sheets --sheet-id <ID>` (replace `<ID>` with your Google Sheet's ID from the URL)
   - Browser will open for authentication (you'll log in to Google and grant permission)
   - **Important**: Make sure you're signing in with the same Google account you added as a test user in step 3
   - Token stored in `~/.config/itbl/token.json` (so you don't have to log in every time)

**Note**: The tool will automatically search for credentials files named:
- `credentials.json`
- `client_secret.json`
- `client_secrets.json`
- `google_credentials.json`

in the config directory or current directory, so you don't need to rename your downloaded file if it has one of these names.

## Development

### Project Structure

```
src/itbl/
  ingest/          # Image loading & preprocessing
  ocr/             # OCR backends (Tesseract, etc.)
  parse/           # Field extraction & classification
  normalize/       # Schema normalization & validation
  review/          # Triage & reporting
  output/          # Writers (CSV, XLSX, Sheets)
  util/            # Config, logging, hashing
  cli.py           # CLI entry point
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_extractors.py

# With coverage
pytest --cov=itbl tests/
```

### Adding Test Fixtures

Place test images in `tests/fixtures/`:
- At least 3-5 per category
- Special sets for checks and bank statements
- Include both clean and low-resolution samples

## Exit Codes

- `0`: Success
- `2`: Staged (needs review, has flagged cells)
- `3`: Fatal error

## Troubleshooting

### Windows-Specific Issues

**"Tesseract not found" error:**
- Make sure Tesseract is installed (see Installation section above)
- Verify it's in your PATH: run `tesseract --version` in PowerShell
- If not found, add Tesseract to your PATH (see Setup section above) or reinstall with "Add to PATH" checked
- After adding to PATH, **close and reopen** your terminal/PowerShell

**Python path issues:**
- If Python is not recognized, make sure Python is installed and added to PATH
- Or use the full path to Python: `C:\Python311\python.exe -m pip install -e .`

**Permission errors:**
- If you get permission errors during installation, try running PowerShell as Administrator
- Or use `pip install --user -e .` to install for your user only

**Chocolatey (choco) not recognized:**
- That's okay! Use Option A (Direct Download) from the Installation section above - it's the recommended method
- Chocolatey is just a convenience tool; you don't need it to install Tesseract

**Google Sheets credentials not found:**
- Make sure the JSON file is named `credentials.json` (or one of: `client_secret.json`, `client_secrets.json`, `google_credentials.json`)
- Place it in `C:\Users\YourUsername\.config\itbl\` or your current working directory
- Or specify the path with `--credentials /path/to/file.json`
- Or set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- The error message will show the exact locations the tool is searching

**"Error 403: access_denied" or "App is being tested" error:**
- This means your OAuth app is in "Testing" mode and your Google account isn't approved
- **IMPORTANT**: You MUST add your Google account as a test user before signing in

**"I don't see 'Test users' section" (Can't find it even with Ctrl+F):**
- **Most likely cause**: Your app is in "Production" mode, not "Testing" mode
- **Fix**: 
  1. On the OAuth consent screen page, look at the TOP for "Publishing status"
  2. If it says "In production" or "Published", look for a "BACK TO TESTING" or "UNPUBLISH" button
  3. Click it to switch back to Testing mode
  4. The "Test users" section should now appear
- **See [docs/NO_TEST_USERS_SECTION.md](docs/NO_TEST_USERS_SECTION.md) for detailed help**

**If you CAN see "Test users" section** - Quick Fix:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Select your project
  3. Go to "APIs & Services" → "OAuth consent screen"
  4. Scroll down to "Test users" section (near the bottom)
  5. Click "ADD USERS"
  6. Enter your **exact Google email address** (check for typos!)
  7. Click "Add" 
  8. **Important**: Scroll to the bottom and click "Save"
  9. Wait a few seconds, then try again
- **Still stuck?** See [docs/TROUBLESHOOTING_403_ERROR.md](docs/TROUBLESHOOTING_403_ERROR.md) for detailed instructions

## Limitations

- **PDF support**: Requires `pdf2image` software (not included by default). You can install it separately if needed.
- **Google Sheets**: Requires internet connection (only for Google Sheets output - CSV/XLSX work completely offline)
- **OCR accuracy**: Depends on image quality - clear, well-lit photos work best
- **Image quality**: Low-resolution or skewed (crooked) images may require manual review

## Need Help Understanding Terms?

See [GLOSSARY.md](GLOSSARY.md) for definitions of technical terms and acronyms like OCR, P&L, CSV, XLSX, API, and more.

## License

MIT

## Contributing

See PRD.md for full requirements and architecture.

