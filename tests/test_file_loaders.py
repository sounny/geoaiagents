import pytest
import json
from file_loaders import load_geojson, _table

def test_load_geojson_feature_collection_two_points():
    geojson_data = json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [15.0, 25.0]
                },
                "properties": {}
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [35.0, 45.0]
                },
                "properties": {}
            }
        ]
    })
    result = load_geojson(geojson_data)
    assert result == _table([(25.0, 15.0), (45.0, 35.0)])
