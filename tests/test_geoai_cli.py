from geoai_cli import TEXT_FIELD_BY_TOOL

def test_text_field_by_tool():
    expected = {
        "load_geojson": "geojson",
        "load_kml": "kml",
        "load_csv": "csv",
    }
    assert TEXT_FIELD_BY_TOOL == expected
