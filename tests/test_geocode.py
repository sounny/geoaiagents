import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from unittest.mock import patch, MagicMock
from geocode import get_coordinates, reverse_geocode_coordinates

@patch('geocode.Nominatim')
@patch('geocode.RateLimiter')
def test_get_coordinates_timeout_handling(mock_rate_limiter_cls, mock_nominatim_cls):
    mock_rate_limiter = MagicMock()
    mock_rate_limiter.side_effect = GeocoderTimedOut("Timeout")
    mock_rate_limiter_cls.return_value = mock_rate_limiter

    address, lat, lon = get_coordinates("Paris, France")

    assert address is None
    assert lat is None
    assert lon is None

@patch('geocode.Nominatim')
@patch('geocode.RateLimiter')
def test_reverse_geocode_service_error_handling(mock_rate_limiter_cls, mock_nominatim_cls):
    mock_rate_limiter = MagicMock()
    mock_rate_limiter.side_effect = GeocoderServiceError("Service error")
    mock_rate_limiter_cls.return_value = mock_rate_limiter

    result = reverse_geocode_coordinates("48.8566,2.3522")

    assert "Not found" in result
