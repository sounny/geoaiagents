import json
import pytest
from file_loaders import load_geojson, _table

def test_load_geojson_feature_collection_two_points():
    """Test that a FeatureCollection with two Point features returns two coordinate rows."""
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [10.0, 20.0]
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [30.0, 40.0]
                }
            }
        ]
    }

    result = load_geojson(json.dumps(geojson_data))

    expected = _table([(20.0, 10.0), (40.0, 30.0)])
    assert result == expected
