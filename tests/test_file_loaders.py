import pytest
from file_loaders import load_csv, _table

def test_load_csv_header_only():
    csv_text = "lat,lon\n"
    assert load_csv(csv_text) == _table([])

def test_load_csv_empty():
    csv_text = ""
    assert load_csv(csv_text) == _table([])
