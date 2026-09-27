import pytest
from geocode import get_coordinates

def test_get_coordinates_rate_limit(mocker):
    # Mock the Nominatim geocoder and RateLimiter to test idempotency and failure cases
    mock_geocode = mocker.patch("geocode._shared_geocode")

    # We want to check if the function handles rate limits/timeouts correctly
    from geopy.exc import GeocoderTimedOut
    mock_geocode.side_effect = GeocoderTimedOut("Timeout")

    # Should not raise, should return (None, None, None)
    address, lat, lon = get_coordinates("Test Location")
    assert address is None
    assert lat is None
    assert lon is None
