import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderParseError
from geocode import get_coordinates, reverse_geocode_coordinates

@pytest.mark.parametrize("exception", [
    GeocoderTimedOut("Mocked timeout"),
    GeocoderServiceError("Mocked service error"),
    GeocoderParseError("Mocked parse error")
])
def test_get_coordinates_timeout_or_error(mocker, exception):
    # Mock _geocode_limiter to raise an exception
    mocker.patch("geocode._geocode_limiter", side_effect=exception)
    result = get_coordinates("Some location")
    assert result == (None, None, None)

@pytest.mark.parametrize("exception", [
    GeocoderTimedOut("Mocked timeout"),
    GeocoderServiceError("Mocked service error"),
    GeocoderParseError("Mocked parse error")
])
def test_reverse_geocode_timeout_or_error(mocker, exception):
    mocker.patch("geocode._reverse_limiter", side_effect=exception)
    result = reverse_geocode_coordinates("40.0, -70.0")
    assert "| 40.0 | -70.0 | Not found |" in result

def test_reverse_geocode_invalid_inputs():
    result = reverse_geocode_coordinates("abc, def; 100, 200")
    assert "_Skipped invalid inputs:_" in result
    assert "abc, def" in result
    assert "100, 200" in result
