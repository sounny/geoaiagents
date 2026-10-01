import pytest
from file_loaders import load_kml

def test_load_kml_malformed_header_only():
    header_only = "| Latitude | Longitude |\n|---------:|----------:|"
    assert load_kml('<not>valid') == header_only
    assert load_kml('') == header_only

def test_load_kml_minimal_point_placemark():
    valid_kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <Point>
      <coordinates>2.35,48.85,0</coordinates>
    </Point>
  </Placemark>
</kml>
"""
    result = load_kml(valid_kml)
    lines = result.split("\n")
    assert len(lines) == 3
    assert "| Latitude | Longitude |" in lines[0]
    assert "| 48.85 | 2.35 |" in result

def test_load_kml_namespace_only_header_only():
    namespace_only_kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
</kml>
"""
    header_only = "| Latitude | Longitude |\n|---------:|----------:|"
    assert load_kml(namespace_only_kml) == header_only
