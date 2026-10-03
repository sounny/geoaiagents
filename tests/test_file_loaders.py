import pytest
from file_loaders import load_csv

def test_load_csv_case_insensitive_headers():
    csv_input = "LAT,LON\n48.8566,2.3522\n"
    expected_table = "| Latitude | Longitude |\n|---------:|----------:|\n| 48.8566 | 2.3522 |"
    assert load_csv(csv_input) == expected_table
