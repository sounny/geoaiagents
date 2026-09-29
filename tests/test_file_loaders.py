import pytest
import file_loaders

def test_load_csv_with_utf8_bom():
    csv_text = "\ufefflat,lon\n48.8566,2.3522"
    result = file_loaders.load_csv(csv_text)
    assert "| 48.8566 | 2.3522 |" in result
