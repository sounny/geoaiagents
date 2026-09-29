import pytest
from file_loaders import load_geojson, _table

def test_load_geojson_linestring_rejection():
    geojson = """
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]]
      },
      "properties": {}
    }
    """
    result = load_geojson(geojson)
    assert "_Skipped invalid inputs:_" in result
    assert "LineString" in result
