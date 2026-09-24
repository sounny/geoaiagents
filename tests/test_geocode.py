import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from geocode import get_coordinates, reverse_geocode_coordinates

def test_get_coordinates_timeout_handling(mocker):
    # Mock the RateLimiter call to raise GeocoderTimedOut
    mock_geocode = mocker.patch('geocode.RateLimiter')
    # The RateLimiter is created and then called, so we mock the __call__ of the returned object
    mock_instance = mock_geocode.return_value
    mock_instance.side_effect = GeocoderTimedOut("Timeout")

    address, lat, lon = get_coordinates("Test Location")

    assert address is None
    assert lat is None
    assert lon is None


def test_reverse_geocode_coordinates_service_error_handling(mocker):
    # Mock parse_coordinate_pairs to return some pairs and no invalid entries
    mocker.patch('geocode.parse_coordinate_pairs', return_value=([(10.0, 20.0)], []))

    # Mock RateLimiter to raise GeocoderServiceError
    mock_reverse = mocker.patch('geocode.RateLimiter')
    mock_instance = mock_reverse.return_value
    mock_instance.side_effect = GeocoderServiceError("Service Error")

    result = reverse_geocode_coordinates("10.0,20.0")

    assert "Not found" in result
