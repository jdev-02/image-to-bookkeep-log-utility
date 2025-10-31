#!/bin/bash
# Example usage scripts for itbl

# Basic parse (offline, CSV output)
itbl parse ./examples/inbox --out ./staging --target csv

# With triage mode (highlights ambiguous cells)
itbl parse ./examples/inbox --triage --target xlsx --out ./staging

# Preview without writing
itbl parse ./examples/inbox --dry-run

# End-to-end with triage
itbl run ./examples/inbox --triage --strict-level medium --target csv --out ./exports

# Google Sheets (requires credentials and sheet-id)
# itbl parse ./examples/inbox --target google-sheets --sheet-id YOUR_SHEET_ID --out ./staging

