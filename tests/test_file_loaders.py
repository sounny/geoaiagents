import pytest
import json
from unittest.mock import patch
from file_loaders import load_geojson, load_kml, load_csv, fetch_geo_boundaries

def test_load_geojson_valid_point():
    geojson_data = json.dumps({
        "type": "Point",
        "coordinates": [-82.3248, 29.6516]
    })
    result = load_geojson(geojson_data)
    assert "| 29.6516 | -82.3248 |" in result

def test_load_geojson_feature_collection():
    geojson_data = json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-81.3792, 28.5383]
                }
            }
        ]
    })
    result = load_geojson(geojson_data)
    assert "| 28.5383 | -81.3792 |" in result

def test_load_geojson_malformed():
    result = load_geojson("invalid json")
    assert "| Latitude | Longitude |" in result
    assert "28.5383" not in result

def test_load_kml_valid():
    kml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <Point>
          <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
        </Point>
      </Placemark>
    </kml>
    """
    result = load_kml(kml_data)
    assert "| 37.42228990140251 | -122.0822035425683 |" in result

def test_load_kml_malformed():
    result = load_kml("<kml>invalid xml")
    assert "| Latitude | Longitude |" in result

def test_load_kml_no_coordinates():
    kml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <Point>
        </Point>
      </Placemark>
    </kml>
    """
    result = load_kml(kml_data)
    assert "| Latitude | Longitude |" in result

def test_load_csv_valid_lat_lon():
    csv_data = "lat,lon\n37.422,-122.082"
    result = load_csv(csv_data)
    assert "| 37.422 | -122.082 |" in result

def test_load_csv_valid_y_x():
    csv_data = "y,x\n37.422,-122.082"
    result = load_csv(csv_data)
    assert "| 37.422 | -122.082 |" in result

def test_load_csv_missing_headers():
    csv_data = "a,b\n1,2"
    result = load_csv(csv_data)
    assert "37.422" not in result

def test_load_csv_malformed():
    result = load_csv("lat,lon\ninvalid,invalid")
    assert "| Latitude | Longitude |" in result

@patch('requests.get')
def test_fetch_geo_boundaries_success(mock_get):
    class MockResponse:
        def __init__(self, json_data, text_data, status_code):
            self.json_data = json_data
            self.text = text_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")

    def mock_get_side_effect(url, timeout=None):
        if "gbOpen" in url:
            return MockResponse({"simplifiedGeometryGeoJSON": "http://mock.url"}, "", 200)
        else:
            return MockResponse({}, json.dumps({"type": "Point", "coordinates": [-122, 37]}), 200)

    mock_get.side_effect = mock_get_side_effect

    result = fetch_geo_boundaries("USA")
    assert "| 37 | -122 |" in result

@patch('requests.get')
def test_fetch_geo_boundaries_error(mock_get):
    mock_get.side_effect = Exception("Network Error")
    result = fetch_geo_boundaries("USA")
    assert "| Latitude | Longitude |" in result

@patch('requests.get')
def test_fetch_geo_boundaries_no_geojson_url(mock_get):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            pass

    mock_get.return_value = MockResponse({}, 200)
    result = fetch_geo_boundaries("USA")
    assert "| Latitude | Longitude |" in result
