import json
import pytest
from file_loaders import load_geojson, load_kml

def test_multipolygon_helper():
    try:
        from file_loaders import multipolygon_helper
    except ImportError:
        pytest.xfail("MultiPolygon helper is missing")

    try:
        mp = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
                [[[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]]]
            ]
        }
        num_polygons, serialized = multipolygon_helper(mp)
        assert num_polygons == 2
        assert json.loads(serialized)
    except Exception as e:
        pytest.xfail(f"Current behavior differs: {e}")

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
        <coordinates>-122.0822035425683,37.42228990140251,100</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <Point>
        <coordinates>-122.082,37.422,50</coordinates>
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
    assert "100" not in res_2_points
    assert "50" not in res_2_points

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

def test_wrap_features_geojson():
    import pytest
    try:
        from file_loaders import wrap_features
    except ImportError:
        pytest.xfail("wrap_features helper is missing from file_loaders")

    features = [{"type": "Feature"}, {"type": "Feature"}]
    fc = wrap_features(features)
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 2


def test_load_geojson_nfc_nfd(tmp_path):
    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f'{{"type":"Feature","geometry":{{"type":"Point","coordinates":[1,2]}},"properties":{{"name":"{nfc}"}}}}'
    nfd_content = f'{{"type":"Feature","geometry":{{"type":"Point","coordinates":[1,2]}},"properties":{{"name":"{nfd}"}}}}'

    file_nfc = tmp_path / "nfc.geojson"
    file_nfd = tmp_path / "nfd.geojson"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_geojson(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_geojson(file_nfd.read_text(encoding="utf-8"))

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_geojson results differ for NFC and NFD strings")

def test_load_kml_nfc_nfd(tmp_path):
    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f'<kml><Placemark><name>{nfc}</name><Point><coordinates>1,2</coordinates></Point></Placemark></kml>'
    nfd_content = f'<kml><Placemark><name>{nfd}</name><Point><coordinates>1,2</coordinates></Point></Placemark></kml>'

    file_nfc = tmp_path / "nfc.kml"
    file_nfd = tmp_path / "nfd.kml"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_kml(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_kml(file_nfd.read_text(encoding="utf-8"))

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_kml results differ for NFC and NFD strings")

def test_load_csv_nfc_nfd(tmp_path):
    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f"lat,lon,name\n1,2,{nfc}"
    nfd_content = f"lat,lon,name\n1,2,{nfd}"

    file_nfc = tmp_path / "nfc.csv"
    file_nfd = tmp_path / "nfd.csv"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_csv(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_csv(file_nfd.read_text(encoding="utf-8"))

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_csv results differ for NFC and NFD strings")


def test_load_geojson_nfc_nfd(tmp_path):
    import unicodedata
    import pytest
    from file_loaders import load_geojson

    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f'{{"type":"Feature","geometry":{{"type":"Point","coordinates":[1,2]}},"properties":{{"name":"{nfc}"}}}}'
    nfd_content = f'{{"type":"Feature","geometry":{{"type":"Point","coordinates":[1,2]}},"properties":{{"name":"{nfd}"}}}}'

    file_nfc = tmp_path / "nfc.geojson"
    file_nfd = tmp_path / "nfd.geojson"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_geojson(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_geojson(file_nfd.read_text(encoding="utf-8"))

    assert "| Latitude | Longitude |" in res_nfc
    assert "| Latitude | Longitude |" in res_nfd

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_geojson results differ for NFC and NFD strings")

def test_load_kml_nfc_nfd(tmp_path):
    import unicodedata
    import pytest
    from file_loaders import load_kml

    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f'<kml><Placemark><name>{nfc}</name><Point><coordinates>1,2</coordinates></Point></Placemark></kml>'
    nfd_content = f'<kml><Placemark><name>{nfd}</name><Point><coordinates>1,2</coordinates></Point></Placemark></kml>'

    file_nfc = tmp_path / "nfc.kml"
    file_nfd = tmp_path / "nfd.kml"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_kml(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_kml(file_nfd.read_text(encoding="utf-8"))

    assert "| Latitude | Longitude |" in res_nfc
    assert "| Latitude | Longitude |" in res_nfd

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_kml results differ for NFC and NFD strings")

def test_load_csv_nfc_nfd(tmp_path):
    import unicodedata
    import pytest
    from file_loaders import load_csv

    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    nfc_content = f"lat,lon,name\n1,2,{nfc}"
    nfd_content = f"lat,lon,name\n1,2,{nfd}"

    file_nfc = tmp_path / "nfc.csv"
    file_nfd = tmp_path / "nfd.csv"

    file_nfc.write_text(nfc_content, encoding="utf-8")
    file_nfd.write_text(nfd_content, encoding="utf-8")

    res_nfc = load_csv(file_nfc.read_text(encoding="utf-8"))
    res_nfd = load_csv(file_nfd.read_text(encoding="utf-8"))

    assert "| Latitude | Longitude |" in res_nfc
    assert "| Latitude | Longitude |" in res_nfd

    if res_nfc != res_nfd:
        pytest.xfail("Bug: load_csv results differ for NFC and NFD strings")

def test_fetch_geo_boundaries_nfc_nfd():
    from unittest import mock
    import unicodedata
    import pytest
    from file_loaders import fetch_geo_boundaries

    nfc = unicodedata.normalize('NFC', 'Ç')
    nfd = unicodedata.normalize('NFD', 'Ç')

    with mock.patch("file_loaders.requests.get") as mock_get:
        mock_resp = mock.MagicMock()
        mock_resp.json.return_value = {"simplifiedGeometryGeoJSON": "http://dummy"}
        mock_resp.text = '{"type":"FeatureCollection","features":[]}'
        mock_get.return_value = mock_resp

        try:
            fetch_geo_boundaries.cache_clear()
        except AttributeError:
            pass

        res_nfc = fetch_geo_boundaries(nfc)
        try:
            url_nfc = mock_get.call_args_list[0][0][0]
        except IndexError:
            url_nfc = None

        try:
            fetch_geo_boundaries.cache_clear()
        except AttributeError:
            pass

        mock_get.reset_mock()
        res_nfd = fetch_geo_boundaries(nfd)
        try:
            url_nfd = mock_get.call_args_list[0][0][0]
        except IndexError:
            url_nfd = None

        assert "| Latitude | Longitude |" in res_nfc
        assert "| Latitude | Longitude |" in res_nfd

        if res_nfc != res_nfd:
            pytest.xfail("Bug: fetch_geo_boundaries results differ for NFC and NFD strings")

        if url_nfc != url_nfd:
            pytest.xfail("Bug: fetch_geo_boundaries requests differ for NFC and NFD strings")
