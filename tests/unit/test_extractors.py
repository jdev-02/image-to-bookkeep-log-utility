"""Unit tests for field extractors."""

import pytest

from itbl.parse.common import extract_amount, extract_date, extract_vendor


def test_extract_date():
    """Test date extraction."""
    # Test various formats
    text1 = "Date: 12/25/2023"
    date, conf = extract_date(text1)
    assert date == "2023-12-25"
    assert conf > 0.8

    text2 = "Invoice date: 2023-12-25"
    date, conf = extract_date(text2)
    assert date == "2023-12-25"
    assert conf > 0.8

    text3 = "No date here"
    date, conf = extract_date(text3)
    assert date is None


def test_extract_amount():
    """Test amount extraction."""
    text1 = "Total: $123.45"
    amount, conf = extract_amount(text1)
    assert amount == 123.45
    assert conf > 0.8

    text2 = "Amount Due: 1,234.56"
    amount, conf = extract_amount(text2)
    assert amount == 1234.56

    text3 = "No amount"
    amount, conf = extract_amount(text3)
    assert amount is None


def test_extract_vendor():
    """Test vendor extraction."""
    text1 = "Office Depot\n123 Main St\nTotal: $50.00"
    vendor, conf = extract_vendor(text1)
    assert vendor is not None
    assert conf > 0.5

    text2 = "Amazon.com Inc\nPurchase"
    vendor, conf = extract_vendor(text2)
    assert "Amazon" in vendor or vendor is not None

