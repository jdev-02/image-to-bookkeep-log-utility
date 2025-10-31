"""Google Sheets writer with batch formatting and notes."""

from pathlib import Path
from typing import Dict, List, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from itbl.output.writer_base import WriterBase
from itbl.util.logging import setup_logging

logger = setup_logging()


class GoogleSheetsWriter(WriterBase):
    """Google Sheets writer with highlighting support."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    CREDENTIALS_FILE = Path.home() / ".config" / "itbl" / "credentials.json"
    TOKEN_FILE = Path.home() / ".config" / "itbl" / "token.json"

    def __init__(self, sheet_id: str, highlight_color: str = "#FFF59D"):
        """
        Initialize Google Sheets writer.
        
        Args:
            sheet_id: Google Sheets ID (from URL)
            highlight_color: Hex color for highlights (default: yellow #FFF59D)
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google API libraries required. Install: pip install google-api-python-client google-auth-oauthlib"
            )
        self.sheet_id = sheet_id
        self.highlight_color = highlight_color
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None

        # Load existing token
        if self.TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(self.TOKEN_FILE), self.SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.CREDENTIALS_FILE}\n"
                        "See README.md for Google Sheets setup instructions."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.CREDENTIALS_FILE), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        self.service = build("sheets", "v4", credentials=creds)

    def _get_tab_id(self, tab_name: str) -> Optional[int]:
        """Get tab/sheet ID by name."""
        try:
            metadata = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            sheets = metadata.get("sheets", [])
            for sheet in sheets:
                if sheet["properties"]["title"] == tab_name:
                    return sheet["properties"]["sheetId"]
        except HttpError as e:
            logger.error(f"Error getting tab ID: {e}")
        return None

    def write(
        self,
        rows: List[Dict],
        output_path: Path,  # Ignored for Sheets
        category: str,
        apply_highlights: bool = False,
    ) -> None:
        """
        Write rows to Google Sheets.
        
        Args:
            rows: List of normalized row dicts
            output_path: Ignored (uses sheet_id)
            category: Category/tab name
            apply_highlights: Whether to apply yellow highlighting
        """
        if not rows:
            return

        # Get or create tab
        tab_id = self._get_tab_id(category)
        if tab_id is None:
            # Create new tab
            requests = [
                {
                    "addSheet": {
                        "properties": {
                            "title": category,
                        }
                    }
                }
            ]
            try:
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id, body={"requests": requests}
                ).execute()
                tab_id = self._get_tab_id(category)
            except HttpError as e:
                logger.error(f"Error creating tab: {e}")
                raise

        # Determine columns (skip hidden fields)
        hidden_prefixes = ["_"]
        sample_row = rows[0]
        all_cols = set(sample_row.keys())
        visible_cols = [
            col for col in all_cols
            if not any(col.startswith(prefix) for prefix in hidden_prefixes)
        ]
        visible_cols = sorted(list(visible_cols))

        # Prepare values
        values = []
        for row in rows:
            row_values = [row.get(col, "") for col in visible_cols]
            values.append(row_values)

        # Append values
        range_name = f"{category}!A:Z"
        body = {"values": values}

        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()
            logger.info(f"Appended {len(values)} rows to {category}")

            # Apply highlighting if requested
            if apply_highlights:
                self._apply_highlights(category, visible_cols, rows)

        except HttpError as e:
            logger.error(f"Error writing to Sheets: {e}")
            raise

    def _apply_highlights(
        self, category: str, columns: List[str], rows: List[Dict]
    ) -> None:
        """Apply yellow highlighting to flagged cells."""
        requests = []
        tab_id = self._get_tab_id(category)

        # Find starting row (get current data range)
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=f"{category}!A:Z"
            ).execute()
            existing_rows = len(result.get("values", []))
            start_row = existing_rows - len(rows) + 1  # +1 for 1-indexed, +1 for header
        except Exception:
            start_row = 2  # Assume header at row 1

        # Build format requests for each flagged cell
        for row_idx, row in enumerate(rows):
            flags = row.get("_flags", [])
            highlight_cells = row.get("_highlight_cells", [])

            if not highlight_cells:
                continue

            for col_name in highlight_cells:
                if col_name not in columns:
                    continue

                col_idx = columns.index(col_name)
                cell_range = f"{category}!{chr(65 + col_idx)}{start_row + row_idx}"

                # Background color
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": tab_id,
                            "startRowIndex": start_row + row_idx - 1,  # 0-indexed
                            "endRowIndex": start_row + row_idx,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": float(int(self.highlight_color[1:3], 16)) / 255.0,
                                    "green": float(int(self.highlight_color[3:5], 16)) / 255.0,
                                    "blue": float(int(self.highlight_color[5:7], 16)) / 255.0,
                                }
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor",
                    }
                })

                # Cell note
                note_text = f"Reason: {', '.join(flags)}\nConfidence: {row.get('_ocr_confidence', 'N/A')}"
                if row.get("_low_conf_tokens"):
                    note_text += "\nLow confidence tokens detected"

                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": tab_id,
                            "startRowIndex": start_row + row_idx - 1,
                            "endRowIndex": start_row + row_idx,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1,
                        },
                        "rows": [
                            {
                                "values": [
                                    {
                                        "note": note_text,
                                    }
                                ]
                            }
                        ],
                        "fields": "note",
                    }
                })

        # Batch update
        if requests:
            try:
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={"requests": requests},
                ).execute()
                logger.info(f"Applied highlighting to {len(requests) // 2} cells")
            except HttpError as e:
                logger.error(f"Error applying highlights: {e}")

