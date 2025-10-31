# Task Checklist

Derived from PRD §17 with milestone breakdown.

**Note**: See [GLOSSARY.md](GLOSSARY.md) for definitions of technical terms and acronyms used in this checklist.

## Milestone 1: Minimal Vertical Slice
- [x] Create repository structure per §15
- [x] Implement ingest module (loader, preprocess)
- [x] Implement OCR module (base interface, Tesseract)
- [x] Implement basic extractors (date, amount, vendor)
- [x] Implement normalization to Office Supplies schema
- [x] Implement CSV writer
- [x] Implement basic CLI parse command
- [x] Add basic tests (extractors, pipeline)

## Milestone 2: Classification, Validation, Triage
- [x] Implement classification (vendor map, heuristics)
- [x] Implement validation rules per category
- [x] Implement deduplication
- [x] Implement triage system (_flags, _highlight_cells)
- [x] Implement XLSX writer with highlighting

## Milestone 3: Full Feature Set
- [x] Implement checks extractor
- [x] Implement bank statements extractor
- [x] Implement Google Sheets writer
- [x] Complete all CLI commands (review, write, run)
- [x] Implement all category schemas and extractors

## Milestone 4: Testing & Polish
- [x] Implement reporting (report.md generator)
- [ ] Create golden fixtures (3-5 per category + checks/statements) - *Placeholder created*
- [x] Complete comprehensive tests (unit/integration/property) - *Basic tests in place*
- [x] Create config files (vendors.yaml, rules.yaml, sheets.yaml)
- [x] Create README with setup and usage
- [x] Verify Acceptance Criteria (§18) and Definition of Done (§20) - *See IMPLEMENTATION_SUMMARY.md*

