import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, geocode_locations

def test_get_coordinates(mocker):
    # Mock RateLimiter to return a mock location
    mock_location = mocker.Mock()
    mock_location.address = "Portland, OR"
    mock_location.latitude = 45.52
    mock_location.longitude = -122.68

    mock_rate_limiter = mocker.patch("geocode.RateLimiter")
    mock_rate_limiter.return_value.return_value = mock_location

    address, lat, lon = get_coordinates("Portland, OR")
    assert address == "Portland, OR"
    assert lat == 45.52
    assert lon == -122.68

    # Mock timeout
    from geopy.exc import GeocoderTimedOut
    mock_rate_limiter.return_value.side_effect = GeocoderTimedOut("Timeout")
    address, lat, lon = get_coordinates("Timeout City")
    assert address is None
    assert lat is None
    assert lon is None

def test_reverse_geocode_coordinates(mocker):
    mock_location = mocker.Mock()
    mock_location.address = "Portland, OR"

    mock_rate_limiter = mocker.patch("geocode.RateLimiter")
    mock_rate_limiter.return_value.return_value = mock_location

    result = reverse_geocode_coordinates("45.52, -122.68")
    assert "| Latitude | Longitude | Address |" in result
    assert "45.52" in result
    assert "-122.68" in result
    assert "Portland, OR" in result

def test_geocode_locations(mocker):
    mock_location = mocker.Mock()
    mock_location.address = "Portland, OR"
    mock_location.latitude = 45.52
    mock_location.longitude = -122.68

    mock_rate_limiter = mocker.patch("geocode.RateLimiter")
    mock_rate_limiter.return_value.return_value = mock_location

    result = geocode_locations("Portland, OR")
    assert "| Input | Matched Address | Latitude | Longitude |" in result
    assert "Portland, OR" in result
    assert "45.52" in result
    assert "-122.68" in result
