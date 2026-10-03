import pytest
from file_loaders import load_csv

def test_load_csv_y_x_aliases():
    csv_text = "y,x\n48.8566,2.3522\n"
    result = load_csv(csv_text)
    assert "48.8566" in result
    assert "2.3522" in result
    assert result.startswith("| Latitude | Longitude |")
