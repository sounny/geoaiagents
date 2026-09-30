import pytest
from file_loaders import load_csv

def test_load_csv_basic():
    csv_text = "latitude,longitude\n48.8566,2.3522\n"
    expected = "| Latitude | Longitude |\n|---------:|----------:|\n| 48.8566 | 2.3522 |"
    assert load_csv(csv_text) == expected
