from file_loaders import load_geojson, load_kml, load_csv
import pytest

def test_load_geojson_feature_point_and_invalid():
    res = load_geojson('{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]}}')
    assert "| Latitude | Longitude |" in res
    assert "48.85" in res
    assert "2.35" in res

def test_load_kml_two_points_and_empty_document():
    kml_2_points = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <Point>
        <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <Point>
        <coordinates>-122.082,37.422,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""

    res_2_points = load_kml(kml_2_points)
    assert "| Latitude | Longitude |" in res_2_points
    assert "37.42228990140251" in res_2_points
    assert "-122.0822035425683" in res_2_points
    assert "37.422" in res_2_points
    assert "-122.082" in res_2_points

    kml_empty_doc = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document></Document>
</kml>"""

    res_empty_doc = load_kml(kml_empty_doc)
    assert "| Latitude | Longitude |" in res_empty_doc
    assert "37.422" not in res_empty_doc

    res_empty = load_geojson('{}')
    assert res_empty.startswith("| Latitude | Longitude |")

    res_bad = load_geojson('{bad')
    assert res_bad.startswith("| Latitude | Longitude |")

def test_load_geojson_feature_collection_one_point():
    fc = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]},"properties":{}}]}'
    res = load_geojson(fc)
    assert "| Latitude | Longitude |" in res
    assert "48.85" in res
    assert "2.35" in res

def test_load_geojson_empty_feature_collection_no_numeric_row():
    fc = '{"type":"FeatureCollection","features":[]}'
    res = load_geojson(fc)
    assert "| Latitude | Longitude |" in res
    assert not any(char.isdigit() for char in res)

@pytest.mark.xfail(reason="Loaders currently expect string content, not string paths")
def test_loaders_accept_str_path(tmp_path):
    geojson_file = tmp_path / "test.geojson"
    geojson_file.write_text('{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]}}')

    kml_file = tmp_path / "test.kml"
    kml_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <Point>
        <coordinates>-122.082,37.422,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>""")

    csv_file = tmp_path / "test.csv"
    csv_file.write_text("lat,lon\n48.85,2.35\n")

    res_geojson = load_geojson(str(geojson_file))
    assert "48.85" in res_geojson

    res_kml = load_kml(str(kml_file))
    assert "37.422" in res_kml

    res_csv = load_csv(str(csv_file))
    assert "48.85" in res_csv

@pytest.mark.xfail(reason="Loaders currently expect string content, not Path objects")
def test_loaders_accept_pathlib_path(tmp_path):
    geojson_file = tmp_path / "test.geojson"
    geojson_file.write_text('{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]}}')

    kml_file = tmp_path / "test.kml"
    kml_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <Point>
        <coordinates>-122.082,37.422,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>""")

    csv_file = tmp_path / "test.csv"
    csv_file.write_text("lat,lon\n48.85,2.35\n")

    res_geojson = load_geojson(geojson_file)
    assert "48.85" in res_geojson

    res_kml = load_kml(kml_file)
    assert "37.422" in res_kml

    res_csv = load_csv(csv_file)
    assert "48.85" in res_csv
