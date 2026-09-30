import json
from file_loaders import load_geojson

def test_load_geojson_multipolygon_rectangle():
    geojson_data = {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [-1.0, -2.0],
                    [1.0, -2.0],
                    [1.0, 2.0],
                    [-1.0, 2.0]
                ]
            ]
        ]
    }
    result = load_geojson(json.dumps(geojson_data))

    # Check that there are at least 4 data rows, plus the 2 header rows
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    assert len(lines) >= 6

    assert "| -2.0 | -1.0 |" in result
    assert "| -2.0 | 1.0 |" in result
    assert "| 2.0 | 1.0 |" in result
    assert "| 2.0 | -1.0 |" in result
