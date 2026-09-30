def test_load_kml_minimal():
    from file_loaders import load_kml
    kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <Point>
        <coordinates>2.3522,48.8566,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""
    result = load_kml(kml)
    assert "| Latitude | Longitude |" in result
    assert "| 48.8566 | 2.3522 |" in result
    assert len(result.strip().split("\n")) == 3
