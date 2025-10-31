"""Integration tests for end-to-end pipeline."""

import tempfile
from pathlib import Path

import pytest

from itbl.cli import parse_command


@pytest.mark.skip(reason="Requires Tesseract and test fixtures")
def test_parse_command_basic():
    """Test basic parse command (requires Tesseract)."""
    # This test requires:
    # 1. Tesseract installed
    # 2. A test image in tests/fixtures/
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path("tests/fixtures/test_receipt.jpg")
        if not input_path.exists():
            pytest.skip("Test fixture not found")

        output_path = Path(tmpdir) / "output"
        output_path.mkdir()

        exit_code = parse_command(
            input_path=input_path,
            output_path=output_path,
            target="csv",
            triage=False,
            dry_run=True,
        )

        assert exit_code == 0 or exit_code == 2  # 0 = success, 2 = staged

