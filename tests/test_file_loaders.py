import pytest
import requests
from file_loaders import fetch_geo_boundaries, _table

def test_fetch_geo_boundaries_success(mocker):
    mock_get = mocker.patch("requests.get")

    # Setup mock responses
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.return_value = None
    mock_resp1.json.return_value = {"simplifiedGeometryGeoJSON": "http://fake-url.com/geo.json"}

    mock_resp2 = mocker.Mock()
    mock_resp2.raise_for_status.return_value = None
    mock_resp2.text = '{"type": "Point", "coordinates": [10.0, 20.0]}'

    mock_get.side_effect = [mock_resp1, mock_resp2]

    result = fetch_geo_boundaries("USA")
    expected = "| Latitude | Longitude |\n|---------:|----------:|\n| 20.0 | 10.0 |"
    assert result == expected

    # Verify requests.get was called with correct arguments
    assert mock_get.call_count == 2
    mock_get.assert_any_call("https://www.geoboundaries.org/api/current/gbOpen/USA/ADM0/", timeout=10)
    mock_get.assert_any_call("http://fake-url.com/geo.json", timeout=10)

def test_fetch_geo_boundaries_first_request_exception(mocker):
    mocker.patch("requests.get", side_effect=requests.RequestException("Network error"))
    result = fetch_geo_boundaries("USA")
    assert result == _table([])

def test_fetch_geo_boundaries_first_request_404(mocker):
    mock_get = mocker.patch("requests.get")
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_resp1

    result = fetch_geo_boundaries("USA")
    assert result == _table([])

def test_fetch_geo_boundaries_missing_geojson_url(mocker):
    mock_get = mocker.patch("requests.get")
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.return_value = None
    mock_resp1.json.return_value = {"some_other_field": "data"}
    mock_get.return_value = mock_resp1

    result = fetch_geo_boundaries("USA")
    assert result == _table([])

def test_fetch_geo_boundaries_second_request_exception(mocker):
    mock_get = mocker.patch("requests.get")
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.return_value = None
    mock_resp1.json.return_value = {"simplifiedGeometryGeoJSON": "http://fake-url.com/geo.json"}

    mock_get.side_effect = [mock_resp1, requests.RequestException("Network error")]

    result = fetch_geo_boundaries("USA")
    assert result == _table([])

def test_fetch_geo_boundaries_second_request_404(mocker):
    mock_get = mocker.patch("requests.get")
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.return_value = None
    mock_resp1.json.return_value = {"simplifiedGeometryGeoJSON": "http://fake-url.com/geo.json"}

    mock_resp2 = mocker.Mock()
    mock_resp2.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

    mock_get.side_effect = [mock_resp1, mock_resp2]

    result = fetch_geo_boundaries("USA")
    assert result == _table([])

def test_fetch_geo_boundaries_invalid_json(mocker):
    mock_get = mocker.patch("requests.get")
    mock_resp1 = mocker.Mock()
    mock_resp1.raise_for_status.return_value = None
    mock_resp1.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)
    mock_get.return_value = mock_resp1

    result = fetch_geo_boundaries("USA")
    assert result == _table([])
