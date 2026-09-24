import pytest
from unittest.mock import MagicMock, patch
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from geocode import get_coordinates, reverse_geocode_coordinates

@patch("geocode.time.sleep")
@patch("geocode.RateLimiter")
def test_get_coordinates_retry(mock_rate_limiter, mock_sleep):
    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 10.0
    mock_location.longitude = 20.0

    mock_geocode_instance = MagicMock()
    mock_rate_limiter.return_value = mock_geocode_instance
    # First call times out, second succeeds
    mock_geocode_instance.side_effect = [GeocoderTimedOut("Timeout"), mock_location]

    mock_sleep.return_value = None

    address, lat, lon = get_coordinates("test query")

    # Now it should retry and succeed
    assert address == "Test Address"
    assert lat == 10.0
    assert lon == 20.0
    assert mock_geocode_instance.call_count == 2
    assert mock_sleep.call_count == 1

@patch("geocode.time.sleep")
@patch("geocode.RateLimiter")
def test_reverse_geocode_retry(mock_rate_limiter, mock_sleep):
    mock_location = MagicMock()
    mock_location.address = "Test Address"

    mock_reverse_instance = MagicMock()
    mock_rate_limiter.return_value = mock_reverse_instance
    mock_reverse_instance.side_effect = [GeocoderTimedOut("Timeout"), mock_location]

    mock_sleep.return_value = None

    res = reverse_geocode_coordinates("10.0, 20.0")

    # Ensure it didn't fail with "Not found"
    assert "Not found" not in res
    assert "Test Address" in res
    assert mock_reverse_instance.call_count == 2
    assert mock_sleep.call_count == 1

@patch("geocode.time.sleep")
@patch("geocode.RateLimiter")
def test_get_coordinates_all_retries_fail(mock_rate_limiter, mock_sleep):
    mock_geocode_instance = MagicMock()
    mock_rate_limiter.return_value = mock_geocode_instance
    mock_geocode_instance.side_effect = GeocoderTimedOut("Timeout")

    mock_sleep.return_value = None

    address, lat, lon = get_coordinates("test query", retries=3)

    assert address is None
    assert lat is None
    assert lon is None
    assert mock_geocode_instance.call_count == 3
    assert mock_sleep.call_count == 2


def test_idempotency_reverse_geocode():
    """Test that repeating the same function call with identical payload gives identical output without changing state."""
    # Assuming the API behaves consistently (which we can mock), the output must be identical.
    with patch('geocode.RateLimiter') as mock_rate_limiter:
        mock_location = MagicMock()
        mock_location.address = "Test Address"
        mock_reverse_instance = MagicMock()
        mock_rate_limiter.return_value = mock_reverse_instance
        mock_reverse_instance.side_effect = [mock_location, mock_location]

        res1 = reverse_geocode_coordinates("10.0, 20.0")
        res2 = reverse_geocode_coordinates("10.0, 20.0")

        assert res1 == res2

def test_idempotency_geocode():
    """Test idempotency for geocode_locations"""
    with patch('geocode.get_coordinates') as mock_get_coords:
        mock_get_coords.return_value = ("Test Address", 10.0, 20.0)

        from geocode import geocode_locations
        res1 = geocode_locations("test query")
        res2 = geocode_locations("test query")

        assert res1 == res2
