import json
from file_loaders import load_geojson, _table

def test_load_geojson_empty_feature_collection():
    """
    Test loading an empty GeoJSON FeatureCollection.
    Assert it loads cleanly and yields no features (resulting in an empty markdown table).
    """
    # Create the empty FeatureCollection
    geojson_data = {"type": "FeatureCollection", "features": []}

    # Call the loader.
    result = load_geojson(json.dumps(geojson_data))

    # Since load_geojson returns a markdown table of features,
    # if it yields no features, the result must be the same as an empty table.
    assert result == _table([])
