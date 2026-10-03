import pytest
from file_loaders import load_kml

def test_load_kml_empty():
    assert load_kml("") == "Error: No coordinates found in KML data."
    assert load_kml("<kml></kml>") == "Error: No coordinates found in KML data."

def test_load_kml_valid():
    kml2 = '<kml xmlns="http://www.opengis.net/kml/2.2"><Placemark><Point><coordinates>1.0,2.0</coordinates></Point></Placemark></kml>'
    res2 = load_kml(kml2)
    assert "| 2.0 | 1.0 |" in res2
