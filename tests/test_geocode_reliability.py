import pytest
from unittest.mock import patch, MagicMock
from geopy.exc import GeocoderTimedOut
from geocode import get_coordinates, reverse_geocode_coordinates, _SHARED_GEOCODE, _SHARED_REVERSE, _SHARED_GEOLOCATOR

def test_shared_rate_limiter_instances():
    # Verify the global RateLimiter instances are configured correctly
    assert _SHARED_GEOCODE.max_retries == 2
    assert _SHARED_GEOCODE.min_delay_seconds == 1

    assert _SHARED_REVERSE.max_retries == 2
    assert _SHARED_REVERSE.min_delay_seconds == 1

    # Assert they use the shared geolocator
    assert _SHARED_GEOCODE.func == _SHARED_GEOLOCATOR.geocode
    assert _SHARED_REVERSE.func == _SHARED_GEOLOCATOR.reverse

@patch('geocode._SHARED_GEOCODE')
def test_get_coordinates_uses_shared_limiter(mock_geocode):
    mock_location = MagicMock()
    mock_location.address = "Paris, France"
    mock_location.latitude = 48.8566
    mock_location.longitude = 2.3522
    mock_geocode.return_value = mock_location

    address, lat, lon = get_coordinates("Paris", timeout=2, language="en")

    mock_geocode.assert_called_once_with(
        "Paris",
        language="en",
        viewbox=None,
        bounded=False,
        timeout=2
    )
    assert address == "Paris, France"
    assert lat == 48.8566
    assert lon == 2.3522

@patch('geocode._SHARED_REVERSE')
def test_reverse_geocode_uses_shared_limiter(mock_reverse):
    mock_location = MagicMock()
    mock_location.address = "Paris, France"
    mock_reverse.return_value = mock_location

    # Simple lat, lon pair
    coordinates_str = "48.8566, 2.3522"

    result = reverse_geocode_coordinates(coordinates_str, timeout=3, language="fr")

    mock_reverse.assert_called_once_with(
        (48.8566, 2.3522),
        language="fr",
        timeout=3
    )

    assert "Paris, France" in result
