import pytest
from file_loaders import load_csv

def test_load_csv_utf8_bom():
    """Test that load_csv correctly handles a CSV string with a UTF-8 BOM."""
    csv_text = "\ufefflat,lon\n48.8566,2.3522"
    result = load_csv(csv_text)

    # We expect a markdown table with one coordinate row.
    assert "| Latitude | Longitude |" in result
    assert "|---------:|----------:|" in result
    assert "| 48.8566 | 2.3522 |" in result

    # It should have exactly 3 lines: header, separator, data row.
    lines = result.strip().split('\n')
    assert len(lines) == 3

def test_load_csv_empty():
    """Test that load_csv handles empty string."""
    assert load_csv("") == "| Latitude | Longitude |\n|---------:|----------:|"

def test_load_csv_no_bom():
    """Test that load_csv handles a CSV string without a BOM."""
    csv_text = "lat,lon\n48.8566,2.3522"
    result = load_csv(csv_text)

    # We expect a markdown table with one coordinate row.
    assert "| 48.8566 | 2.3522 |" in result
