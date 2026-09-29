from file_loaders import load_kml

def test_load_kml_positive():
    kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <Point>
      <coordinates>2.3,48.8,0</coordinates>
    </Point>
  </Placemark>
</kml>"""
    result = load_kml(kml)
    assert "48.8" in result
    assert "2.3" in result
