import pytest
from file_loaders import load_geojson, load_kml, load_csv, fetch_geo_boundaries

def test_load_geojson():
    # Valid Point
    geojson_valid = '{"type": "Point", "coordinates": [-122.6, 45.5]}'
    result = load_geojson(geojson_valid)
    assert "45.5" in result
    assert "-122.6" in result

    # Valid FeatureCollection
    geojson_fc = '''{
      "type": "FeatureCollection",
      "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-118.25, 34.05]}}
      ]
    }'''
    result = load_geojson(geojson_fc)
    assert "34.05" in result
    assert "-118.25" in result

    # Invalid JSON
    assert "Latitude | Longitude" in load_geojson("not a json")

def test_load_kml():
    kml_valid = '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <Point>
          <coordinates>-122.6,45.5,0</coordinates>
        </Point>
      </Placemark>
    </kml>'''
    result = load_kml(kml_valid)
    assert "45.5" in result
    assert "-122.6" in result

    # Invalid XML
    assert "Latitude | Longitude" in load_kml("not a xml")

def test_load_csv():
    csv_valid = "lat,lon\n45.5,-122.6\n34.05,-118.25"
    result = load_csv(csv_valid)
    assert "45.5" in result
    assert "-122.6" in result
    assert "34.05" in result
    assert "-118.25" in result

    # Alternate headers
    csv_alt = "latitude,longitude\n10,20"
    result = load_csv(csv_alt)
    assert "10.0" in result
    assert "20.0" in result

    # Invalid CSV
    assert "Latitude | Longitude" in load_csv("not a csv")

def test_fetch_geo_boundaries(mocker):
    # Mock requests.get
    mock_get = mocker.patch("requests.get")
    mock_response_1 = mocker.Mock()
    mock_response_1.json.return_value = {"simplifiedGeometryGeoJSON": "http://fake.url"}

    mock_response_2 = mocker.Mock()
    mock_response_2.text = '{"type": "Point", "coordinates": [-122.6, 45.5]}'

    mock_get.side_effect = [mock_response_1, mock_response_2]

    result = fetch_geo_boundaries("USA", "ADM0")
    assert "45.5" in result
    assert "-122.6" in result

    # Mock requests.get failure
    mock_get.side_effect = Exception("Network Error")
    result = fetch_geo_boundaries("USA", "ADM0")
    assert "Latitude | Longitude" in result
    assert "-122.6" not in result
