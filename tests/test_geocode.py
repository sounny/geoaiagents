import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from unittest.mock import Mock

from geocode import get_coordinates, reverse_geocode_coordinates

def test_get_coordinates_retry(mocker):
    # Instead of mocking RateLimiter wrapper, let's test if the kwargs are passed correctly
    mock_rate_limiter = mocker.patch("geocode.RateLimiter")

    # Just need it to return something so get_coordinates doesn't fail
    mock_callable = mocker.Mock(return_value=mocker.Mock(address="Test Address", latitude=1.0, longitude=2.0))
    mock_rate_limiter.return_value = mock_callable

    get_coordinates("Test Location")

    # Check that RateLimiter was initialized with max_retries=2
    mock_rate_limiter.assert_called_once()
    _, kwargs = mock_rate_limiter.call_args
    assert kwargs.get("max_retries") == 2

def test_reverse_geocode_coordinates_retry(mocker):
    mock_rate_limiter = mocker.patch("geocode.RateLimiter")
    mock_callable = mocker.Mock(return_value=mocker.Mock(address="Test Address"))
    mock_rate_limiter.return_value = mock_callable

    reverse_geocode_coordinates("0,0")

    mock_rate_limiter.assert_called_once()
    _, kwargs = mock_rate_limiter.call_args
    assert kwargs.get("max_retries") == 2
