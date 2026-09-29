import pytest
from file_loaders import load_csv, _table

def test_load_csv_bom():
    csv_text = "\ufefflat,lon\n48.8566,2.3522"
    result = load_csv(csv_text)
    expected = _table([(48.8566, 2.3522)])
    assert result == expected
