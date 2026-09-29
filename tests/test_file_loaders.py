import pytest
from file_loaders import load_csv, _table

def test_load_csv_yx_aliases():
    csv_text = "y,x\n34.05,-118.25\n"
    result = load_csv(csv_text)
    assert "| 34.05 | -118.25 |" in result

def test_load_csv_missing_columns():
    csv_text = "a,b\n1,2\n"
    result = load_csv(csv_text)
    assert result == _table([])

def test_load_csv_header_only():
    csv_text = "y,x\n"
    result = load_csv(csv_text)
    assert result == _table([])
