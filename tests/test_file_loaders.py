import pytest
from file_loaders import load_kml

def test_load_kml_malformed_xml():
    expected = "| Latitude | Longitude |\n|---------:|----------:|"
    assert load_kml('<not-valid-kml') == expected

def test_load_kml_empty_string():
    expected = "| Latitude | Longitude |\n|---------:|----------:|"
    assert load_kml('') == expected
