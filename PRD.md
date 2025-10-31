PRD: image-to-bookkeep-log (with Triage & Yellow-Highlight Workflow)

A utility to ingest local images (receipts, checks, invoices, bank statements), parse them entirely offline, and populate a P&L bookkeeping ledger (Google Sheets or local Excel/CSV), with clear mappings to predefined categories/tabs, cell-level ambiguity highlighting (yellow) for manual investigation, and a fast Initial Triage mode for “easy” uploads.

1) Goals & Non-Goals
Goals

Accept local files (.jpg/.jpeg/.png/.tiff/.heic, optional .pdf) via CLI or folder path.

Perform fully offline OCR and parsing (privacy-first).

Parse and normalize fields into the following P&L tabs:

Revenue — Date, Customer/Source, Description, Invoice #, Amount, Payment Method

COGS — Date, Vendor/Supplier, Item/Description, Product Line, Amount, Payment Method

R&D — Date, Vendor/Payee, Item/Description, Business Purpose, Amount, Payment Method

Professional Services — Date, Vendor/Provider, Service/Description, Business Purpose, Amount, Payment Method

Transportation — Date, From, To, Business Purpose, Miles, Rate/Mile, Amount

Home Office — Expense Type, Total Annual, Business %, Office %, Calculation, Deductible Amount

Phone & Internet — Service Type, Monthly Cost, Annual Cost, Business %, Calculation, Deductible Amount

Office Supplies — Date, Vendor, Item/Description, Business Purpose, Amount, Payment Method

Marketing — Date, Vendor/Platform, Campaign/Description, Marketing Type, Amount, Payment Method

Insurance — Date, Insurance Company, Policy Type, Coverage Period, Amount, Payment Method

Bank Fees — Date, Financial Institution, Fee Type, Business Purpose, Amount, Account

Summary — Category, Amount, Notes, Tax Treatment (rollup)

Personal Expense workbook — rows tagged as personal; indicates checks to cut from business

Provide CLI and modular Python library; support Google Sheets and local CSV/XLSX outputs.

Data validation, audit logs, idempotent runs (deduplication).

New: Cell-level ambiguity highlighting (yellow) for manual investigation in Sheets/XLSX; annotations for CSV.

New: Initial Triage mode for quick, minimal-effort parsing of checks and bank statements.

Non-Goals

Cloud OCR/LLM usage.

Automated tax filing or legal/tax advice.

Full bank statement reconciliation (beyond basic line extraction & categorization hints).

2) User Stories

As J, I run itbl parse ./inbox/ --triage to OCR images offline, extract fields, and produce a workbook where only ambiguous cells are yellow with notes.

As J, I run itbl write --target google-sheets to append validated rows to my existing Sheet tabs with yellow highlights and cell notes for uncertain fields.

As J, I maintain a vendor/category mapping (YAML) so vendors auto-route to categories and default field hints (reducing yellow flags over time).

As J, I can dry-run (--dry-run) to preview rows and flags before writes, and use interactive fix (--fix) for edge cases.

As J, I can export a Personal Expense list to cut checks from the business.

3) Functional Requirements
Input

Accept path(s)/globs to files and folders.

Supported: .jpg/.jpeg/.png/.tiff/.heic and optional .pdf (split multipage).

Optional sidecar metadata (.json/.yaml) per file for category/field overrides.

Preprocessing

Auto-rotate, de-skew, denoise, binarize; page split for PDFs.

Configurable DPI, thresholding, language (default: English).

OCR (Offline)

Default Tesseract 5 (CPU). Pluggable backends (PaddleOCR/docTR) behind a common interface.

Parsing

Extract: Vendor/Payee, Document Date, Total/Amount, Taxes, Line items (when present), Invoice #, Payment Method.

Special extractors:

Coverage Period (insurance): date ranges.

Mileage (transportation): miles, rate, amount (compute one if two present).

Checks: Date, Payee, Amount (digits & words cross-check), Check #, Memo.

Bank Statements: Date, Description, Amount (+/−), Balance (optional).

Classification → P&L Category

Priority: (1) Sidecar override → (2) Vendor map → (3) Keyword heuristics → (4) Unclassified review.

Confidence score per field and row.

Normalization & Validation

Normalize to tab schemas (listed in §7).

Validate: required fields, date formats, numeric coercions, sign conventions; per-category rules (see §11).

Ambiguity Detection & Triage (New)

Per-field ambiguity conditions → yellow-highlight cell:

OCR token confidence < 0.80.

Multiple candidates with small delta (e.g., amounts within 5%).

Parse failures (date/number) → blank cell + yellow + note.

Rule violations (e.g., negative amount where not allowed).

Category disagreement (vendor map vs. keyword router).

Payment Method unresolved but card tokens detected.

Transportation missing complements (e.g., Miles only).

Initial Triage mode (--triage):

Optimized for checks and bank statements; fast heuristics, minimal structure.

If value plausible, write it and paint yellow; if not plausible, write blank + yellow + note.

For uncertain category, write best guess (configurable) and mark yellow with top-3 candidates in the note.

Deduplication

Content hash plus (vendor, date, amount) triad. Idempotent appends.

Output

Google Sheets: append values; batch-style background color to yellow (#FFF59D) for flagged cells; add cell notes with reason(s).

XLSX: write values with yellow fill for flagged cells; add comments with reason(s) where supported.

CSV: no colors → add _triage column listing flagged fields; optional inline wrappers <<REVIEW: reason>> value with --csv-annotate.

Summary tab: rollup by category with optional “Tax Treatment” mapping.

Personal Expense workbook: export entries tagged personal=true → payee, amount, reason, and check status.

Artifacts & Logs

report.md: run summary (files processed, success/staged/unclassified), cell-level triage metrics, top vendors to map, common failures.

Parse log (.jsonl), validation report (CSV/MD), per-run audit with row IDs.

4) Non-Functional Requirements

Privacy: no network during OCR/parse unless writing to Google Sheets.

Determinism: same input + config → same output.

Performance: ~1–3s per standard receipt/check on CPU; batch-parallelizable.

Extensibility: pluggable OCR, extractors, writers.

Testability: golden fixtures; unit/integration/property tests.

5) System Architecture
+---------------------------+
| CLI (itbl)                |
|  - parse / write / review |
+------------+--------------+
             |
             v
+---------------------------+        +------------------------+
| Ingestion & Preprocess    |        | Config & Mappings      |
|  - rotate/deskew/denoise  |<------>| vendors.yaml           |
|  - pdf split              |        | categories.yaml        |
+-------------+-------------+        | rules.yaml             |
              |                      +------------------------+
              v
+---------------------------+
| OCR Engine (Offline)      |
|  - text + layout          |
+-------------+-------------+
              |
              v
+---------------------------+
| Parser & Classifier       |
|  - common + specializers  |
|  - checks/statements      |
+-------------+-------------+
              |
              v
+---------------------------+        +------------------------+
| Normalizer & Validator    |------->| Review Queue & Triage  |
|  - per-tab schemas        |        | _flags/_highlight_cells|
+-------------+-------------+        +------------------------+
              |
              v
+---------------------------+        +------------------------+
| Writer Layer              |------->| Google Sheets / XLSX   |
|  - csv/xlsx/sheets        |        | CSV annotations        |
+---------------------------+        +------------------------+

6) Architectural Decision Matrix
Decision Area	Option	Offline	Accuracy	Layout	Speed	License	Complexity	Chosen	Rationale
OCR Engine	Tesseract 5 + OpenCV	✅	◑	◑	◑	Apache 2	Low	✅	Mature, free, reliable for receipts/checks.
	PaddleOCR (CPU)	✅	◕	◕	◑	Apache 2	Med	☐	Higher accuracy; optional backend.
	docTR (PyTorch)	✅	◕	◕	◐	MIT	Med/High	☐	Strong layout; heavier.
Table Extraction	Heuristics/regex	✅	◑	◑	◕	—	Low	✅	Simple + robust enough for triage.
Output	Google Sheets API	❌	—	—	—	—	Med	✅	Primary collaborative target.
	Local CSV/XLSX	✅	—	—	—	—	Low	✅	Offline-first staging.
Highlighting	Batch Sheets formatting	❌	—	—	—	—	Med	✅	Precise cell styling + notes.
CSV Flags	_triage + wrappers	✅	—	—	—	—	Low	✅	Preserve signals without colors.
Triage Scope	Checks & Statements first	—	—	—	—	—	—	✅	High ROI for business owners.
7) Data Schemas (Normalized Rows)

Hidden fields on all rows (not shown in business tabs unless configured):
_row_id (UUID), _source_file, _hash, _confidence, _created_at, _flags, _highlight_cells.

Revenue

Date, Customer/Source, Description, Invoice #, Amount, Payment Method

COGS

Date, Vendor/Supplier, Item/Description, Product Line, Amount, Payment Method

R&D

Date, Vendor/Payee, Item/Description, Business Purpose, Amount, Payment Method

Professional Services

Date, Vendor/Provider, Service/Description, Business Purpose, Amount, Payment Method

Transportation

Date, From, To, Business Purpose, Miles, Rate/Mile, Amount

Home Office

Expense Type, Total Annual, Business %, Office %, Calculation, Deductible Amount

Phone & Internet

Service Type, Monthly Cost, Annual Cost, Business %, Calculation, Deductible Amount

Office Supplies

Date, Vendor, Item/Description, Business Purpose, Amount, Payment Method

Marketing

Date, Vendor/Platform, Campaign/Description, Marketing Type, Amount, Payment Method

Insurance

Date, Insurance Company, Policy Type, Coverage Period, Amount, Payment Method

Bank Fees

Date, Financial Institution, Fee Type, Business Purpose, Amount, Account

Summary (generated)

Category, Amount, Notes, Tax Treatment

Personal Expense (generated)

Date, Vendor, Description, Amount, Reason/Notes, Check To, Status (Pending/Cleared)

8) Classification & Field Extraction
Vendor/Category Resolution

vendors.yaml:

- match: "Amazon Web Services"
  category: COGS
  hints:
    product_line: "Cloud"
    payment_method: "ACH"
- match: "Blue Cross"
  category: Insurance
  hints:
    policy_type: "Health"
- match_regex: "(?i)google ads|meta ads|x ads"
  category: Marketing
  hints:
    marketing_type: "Paid Ads"


Priority: Sidecar → Vendor map → Heuristics → Manual review.

Key Patterns

Date: %m/%d/%Y, %Y-%m-%d, %b %d, %Y → normalized to YYYY-MM-DD.

Amount: last of Total|Amount Due|Grand Total.

Invoice #: Invoice|Inv + alphanum.

Payment Method: VISA ****, AMEX, Mastercard, ACH, Cash, PayPal.

Coverage Period: MM/DD/YYYY - MM/DD/YYYY.

Mileage/Rate: (\d+(\.\d+)?) miles, rate per mile $0.xx.

Checks: cross-check amount in words vs digits; mismatch → both yellow.

Bank Statements: detect sign, common markers (Withdrawal, Deposit, ACH, Check ####, Card ####).

9) Ambiguity & Highlighting (Detailed)

Thresholds (default, tunable via --strict-level):

low_conf: OCR token confidence < 0.80.

multi_candidates: small deltas (< 5% for amounts; Levenshtein or cosine similarity for vendors).

parse_error: date/number could not parse → blank + yellow + note.

rule_violation: violates validation rule (e.g., negative amount).

category_conflict: vendor map vs keyword heuristics disagree.

incomplete: missing complementary fields (e.g., Miles without Rate/Amount).

Notes/comments show: reason code, confidence, and top alternatives (where relevant).

CSV: _triage column contains list of flagged fields; optional inline wrappers.

10) CLI
# Parse images and stage normalized outputs (no network)
itbl parse ./inbox --out ./staging --engine tesseract --dry-run

# Initial triage path for checks & bank statements with yellow highlights
itbl parse ./inbox --triage --target xlsx --out ./staging

# Apply highlights and notes to Google Sheets
itbl write --target google-sheets --sheet-id <ID> --apply-highlights

# End-to-end, local-first, medium strictness
itbl run ./inbox --triage --strict-level medium --target csv --out ./exports

# Options
itbl parse ./inbox \
  --highlight-color "#FFF59D" \
  --csv-annotate \
  --category-force <Category> \
  --no-network \
  --parallel 4 \
  --config ./config/


New Flags

--triage

--apply-highlights

--highlight-color <hex> (default #FFF59D)

--csv-annotate

--strict-level {low|medium|high}

11) Validation Rules (per Category)

Shared: required fields present; dates parse and are not in the far future; amounts numeric; currency normalized; duplicates blocked.

Transportation: (Miles AND Rate/Mile) OR Amount required; compute missing one if two present.

Home Office / Phone & Internet: recompute Deductible Amount from percentages; ensure Calculation explains formula.

Bank Fees/Revenue/COGS: strict on date/amount; flag aggressively if ambiguous.

Marketing/Pro Services: treat Description leniently unless empty.

12) Output Writers

Sheets Writer: batch append values → batch format flagged cells (#FFF59D) → add notes with reasons; exponential backoff for rate limits.

XLSX Writer: apply yellow fill and cell comments; maintain local cache & run manifest for audit.

CSV Writer: add _triage column; optional inline <<REVIEW: reason>> value wrappers; configurable.

13) Security & Privacy

Strict offline OCR/parse.

--no-network guard to enforce offline mode.

Redact PAN/PII in logs via regex masks.

Configurable cache directory; .gitignore sensitive outputs.

14) Testing Strategy

Golden fixtures: at least 3–5 samples per category; specific sets for checks and bank statements (clean/low-res).

Unit tests: extractors (date/amount/coverage/mileage), vendor map resolution, classification precedence, validation rules.

Integration tests: end-to-end on a small “inbox”; snapshot normalized CSV/XLSX; verify highlighted cells and notes.

Property tests: currency/number parsing with randomized separators and formats.

Performance: benchmark batch parsing on CPU with parallelism.

15) Repository Structure (Proposal)
image-to-bookkeep-log/
  src/itbl/
    __init__.py
    cli.py
    ingest/
      loader.py
      preprocess.py
    ocr/
      base.py
      tesseract.py
      paddle.py
    parse/
      common.py
      extractors.py
      classify.py
      categories/
        revenue.py
        cogs.py
        rnd.py
        pro_services.py
        transportation.py
        home_office.py
        phone_internet.py
        office_supplies.py
        marketing.py
        insurance.py
        bank_fees.py
        checks.py
        bank_statements.py
    normalize/
      schemas.py
      validate.py
      dedupe.py
    review/
      report.py
      interactive.py
      triage.py
    output/
      writer_base.py
      csv_writer.py
      xlsx_writer.py
      gsheet_writer.py
    util/
      config.py
      hashing.py
      logging.py
  config/
    vendors.yaml
    rules.yaml
    sheets.yaml
  tests/
    fixtures/
    unit/
    integration/
  examples/
    inbox/
  README.md

16) Config Examples

sheets.yaml

tabs:
  Revenue: ["Date","Customer/Source","Description","Invoice #","Amount","Payment Method"]
  COGS: ["Date","Vendor/Supplier","Item/Description","Product Line","Amount","Payment Method"]
  R&D: ["Date","Vendor/Payee","Item/Description","Business Purpose","Amount","Payment Method"]
  Professional Services: ["Date","Vendor/Provider","Service/Description","Business Purpose","Amount","Payment Method"]
  Transportation: ["Date","From","To","Business Purpose","Miles","Rate/Mile","Amount"]
  Home Office: ["Expense Type","Total Annual","Business %","Office %","Calculation","Deductible Amount"]
  Phone & Internet: ["Service Type","Monthly Cost","Annual Cost","Business %","Calculation","Deductible Amount"]
  Office Supplies: ["Date","Vendor","Item/Description","Business Purpose","Amount","Payment Method"]
  Marketing: ["Date","Vendor/Platform","Campaign/Description","Marketing Type","Amount","Payment Method"]
  Insurance: ["Date","Insurance Company","Policy Type","Coverage Period","Amount","Payment Method"]
  Bank Fees: ["Date","Financial Institution","Fee Type","Business Purpose","Amount","Account"]
  Summary: ["Category","Amount","Notes","Tax Treatment"]
personal_expense_tab: "Personal Expenses"
highlight:
  color: "#FFF59D"
  strict_level: "medium"


rules.yaml

date_formats: ["%m/%d/%Y","%Y-%m-%d","%b %d, %Y"]
currency_symbols: ["$", "USD"]
triage:
  ocr_conf_threshold: 0.80
  amount_delta_pct: 0.05
  reasons: ["low_conf","multi_candidates","parse_error","rule_violation","category_conflict","incomplete"]
summary_tax_treatment:
  Marketing: "Deductible"
  R&D: "Deductible"
  Home Office: "Deductible (limitations apply)"
  Insurance: "Varies by policy"
csv:
  annotate_inline: true
  triage_column: "_triage"


vendors.yaml

- match: "Amazon Web Services"
  category: "COGS"
  hints:
    product_line: "Cloud"
    payment_method: "ACH"
- match: "Blue Cross"
  category: "Insurance"
  hints:
    policy_type: "Health"
- match_regex: "(?i)google ads|meta ads|x ads"
  category: "Marketing"
  hints:
    marketing_type: "Paid Ads"

17) Task Breakdown (Issues Backlog)
Epic: OCR & Parsing

 Tesseract wrapper (DPI/psm/oem), preprocessing (deskew, binarize, denoise, rotate).

 Extractors: date, amount, vendor, invoice #, payment method, coverage period, mileage.

Epic: Classification

 Vendor map loader + exact/contains/regex matching.

 Keyword heuristics per category.

 Confidence scoring per field & row.

Epic: Normalization & Validation

 Define schemas per tab; row builders.

 Validation rules + error messages.

 Deduping: hash + vendor/date/amount.

Epic: Triage & Highlight (New)

 Per-field _flags with reason codes + details.

 Compute _highlight_cells; expose to writers.

 Sheets writer: batch background color + cell notes.

 XLSX writer: yellow fills + cell comments.

 CSV writer: _triage column + optional inline wrappers.

 CLI flags: --triage, --apply-highlights, --highlight-color, --strict-level.

Epic: Simple Doc Extractors (New)

 Checks: payee/date/amount (digits vs words), check #, memo.

 Bank statements: date/description/amount/balance; sign detection.

 Category suggestion + yellow if uncertain (top-3 in note).

Epic: Reporting

 report.md: cell-level triage counts by tab/field; top reasons; suggested vendor-map additions.

 Include examples of flagged cells and recommendations.

Epic: CLI & UX

 parse, review, write, run commands; --dry-run, --no-network, --parallel, --config.

 Interactive fix mode (--fix) for staged items.

Epic: QA & Tooling

 Golden fixtures per category; special sets for checks/statements.

 Unit/integration/property tests; CI workflow.

 Performance profiling & threshold tuning.

Epic: Enhancements (Phase 2)

 Optional PaddleOCR/docTR backend plug-in.

 LayoutParser integration for tables.

 Bank statement reconciliation (pilot).

 Lightweight local UI (Streamlit/Tauri) for review.

18) Acceptance Criteria

Triage highlighting: Running
itbl parse ./inbox --triage --target xlsx produces workbooks where ambiguous cells are yellow and contain comments with reasons; non-ambiguous cells are unstyled.

Sheets formatting: itbl write --target google-sheets --apply-highlights appends rows and applies yellow (#FFF59D) to flagged cells with cell notes.

CSV annotations: With --csv-annotate, _triage column lists flagged fields; flagged cells optionally wrapped as <<REVIEW: reason>> value.

Report: report.md includes cell-level triage metrics and top reasons; suggests vendor-map additions.

Accuracy: On a test batch of checks/statements, ≥95% of obvious fields (date, amount) are not flagged; ambiguous cases are correctly highlighted.

Idempotency: Re-running on same dataset does not duplicate rows unless --force.

19) Risks & Mitigations

Over-highlighting noise → --strict-level control; vendor-map growth reduces flags; tuned thresholds.

Sheets API limits → batch updates, compact ranges, graceful fallback to row notes.

OCR on low-quality images → stronger preprocessing; optional advanced backends; interactive fixes.

20) Definition of Done

End-to-end offline to CSV/XLSX; optional Google Sheets append with yellow highlights and notes.

Configurable vendor/category mappings; reproducible test run with fixtures.

report.md includes cell-level triage section.

Comprehensive unit/integration tests; CI green.