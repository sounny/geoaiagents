import pytest
from file_loaders import load_kml, load_geojson, load_csv

def test_load_kml_normal():
    kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Simple placemark</name>
      <Point>
        <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""
    res = load_kml(kml)
    assert "| 37.42228990140251 | -122.0822035425683 |" in res

def test_load_kml_xxe():
    xxe_payload = """<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>XXE</name>
      <Point>
        <coordinates>&xxe;,0,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""
    res = load_kml(xxe_payload)
    # The defusedxml should raise an exception which gets caught and returns an empty table
    assert "| Latitude | Longitude |" in res
    assert "&xxe;" not in res
    # Should not crash but return empty table
    assert res.count("\n") == 1 # Just the header lines
