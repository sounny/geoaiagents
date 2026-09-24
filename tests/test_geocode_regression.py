import pytest
import time
from geocode import geocode_locations, reverse_geocode_coordinates, get_coordinates
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def test_geocode_locations_enforces_rate_limit(mocker):
    # Enforces that rate limits are preserved across multiple calls
    mock_nominatim = mocker.patch('geocode.Nominatim')
    mock_instance = mock_nominatim.return_value
    mock_instance.geocode.return_value = mocker.Mock(address="A", latitude=1.0, longitude=2.0)

    mock_sleep = mocker.patch('geopy.extra.rate_limiter.sleep')

    geocode_locations("loc1\nloc2\nloc3")
    assert mock_sleep.call_count >= 2, "RateLimiter did not sleep between requests"

def test_stale_results_cleanup(mocker):
    # Test that failed lookups do not poison subsequent valid lookups (stale/duplicate fix)
    mock_nominatim = mocker.patch('geocode.Nominatim')
    mock_instance = mock_nominatim.return_value

    # First fails, second succeeds
    mock_instance.geocode.side_effect = [
        GeocoderTimedOut("Timeout"),
        GeocoderTimedOut("Timeout"),
        GeocoderTimedOut("Timeout"), # 1 attempt + 2 retries
        mocker.Mock(address="Valid", latitude=1.0, longitude=2.0)
    ]

    res = geocode_locations("loc_fail\nloc_success")
    assert "Not found" in res
    assert "Valid" in res

def test_retries_on_service_error(mocker):
    # RateLimiter should retry when hitting a service error
    mock_nominatim = mocker.patch('geocode.Nominatim')
    mock_instance = mock_nominatim.return_value

    # Fail once, then succeed
    mock_instance.geocode.side_effect = [
        GeocoderServiceError("Error"),
        mocker.Mock(address="Retry Success", latitude=3.0, longitude=4.0)
    ]

    res = geocode_locations("loc_retry")
    assert "Retry Success" in res
    # Ensure it was called twice due to retry
    assert mock_instance.geocode.call_count == 2
