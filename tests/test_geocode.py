import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geocode import get_coordinates

def test_get_coordinates_timeout_handling(mocker):
    # Mock Nominatim class to return an instance with a mocked geocode method
    mock_nominatim = mocker.patch('geocode.Nominatim')
    mock_geolocator = mock_nominatim.return_value

    # We also need to mock RateLimiter since it wraps the geocode method
    mock_ratelimiter = mocker.patch('geocode.RateLimiter')
    # Make the RateLimiter instance raise a GeocoderTimedOut when called
    mock_ratelimiter.return_value.side_effect = GeocoderTimedOut("Timeout")

    # Execute
    address, lat, lon = get_coordinates("Austin, TX")

    # Assert
    assert address is None
    assert lat is None
    assert lon is None

def test_get_coordinates_service_error_handling(mocker):
    # Mock Nominatim class to return an instance with a mocked geocode method
    mock_nominatim = mocker.patch('geocode.Nominatim')
    mock_geolocator = mock_nominatim.return_value

    # We also need to mock RateLimiter since it wraps the geocode method
    mock_ratelimiter = mocker.patch('geocode.RateLimiter')
    # Make the RateLimiter instance raise a GeocoderServiceError when called
    mock_ratelimiter.return_value.side_effect = GeocoderServiceError("Service error")

    # Execute
    address, lat, lon = get_coordinates("Austin, TX")

    # Assert
    assert address is None
    assert lat is None
    assert lon is None
