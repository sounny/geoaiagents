import pytest
from geocode import get_coordinates, reverse_geocode_coordinates
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

@pytest.mark.parametrize("exception", [
    GeocoderTimedOut("Mocked timeout"),
    GeocoderServiceError("Mocked service error")
])
def test_get_coordinates_timeout_or_error(mocker, exception):
    # Mock _geocode_limiter to raise an exception
    mocker.patch("geocode._geocode_limiter", side_effect=exception)
    result = get_coordinates("Some location")
    assert result == (None, None, None)

@pytest.mark.parametrize("exception", [
    GeocoderTimedOut("Mocked timeout"),
    GeocoderServiceError("Mocked service error")
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

class MockLocation:
    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

def test_get_coordinates_success_and_kwargs(mocker):
    mock_loc = MockLocation("123 Main St", 40.0, -70.0)
    mock_limiter = mocker.patch("geocode._geocode_limiter", return_value=mock_loc)

    bbox = (-75.0, 35.0, -65.0, 45.0)
    result = get_coordinates("Some location", language="fr", bounding_box=bbox, timeout=2)

    assert result == ("123 Main St", 40.0, -70.0)
    mock_limiter.assert_called_once_with(
        "Some location",
        language="fr",
        viewbox=bbox,
        bounded=True,
        timeout=2
    )

def test_get_coordinates_not_found(mocker):
    mocker.patch("geocode._geocode_limiter", return_value=None)
    result = get_coordinates("Unknown location")
    assert result == (None, None, None)

def test_reverse_geocode_success_and_kwargs(mocker):
    mock_loc = MockLocation("123 Main St", 40.0, -70.0)
    mock_limiter = mocker.patch("geocode._reverse_limiter", return_value=mock_loc)

    result = reverse_geocode_coordinates("40.0, -70.0", language="es", timeout=3)

    mock_limiter.assert_called_once_with((40.0, -70.0), language="es", timeout=3)
    assert "| 40.0 | -70.0 | 123 Main St |" in result
    assert "Latitude" in result
    assert "Longitude" in result
    assert "Address" in result

def test_reverse_geocode_empty_coordinates():
    result = reverse_geocode_coordinates("")

    # It should just have the table headers and no extra lines
    assert "| Latitude | Longitude | Address |" in result
    assert "|---------:|----------:|---------|" in result

    # Should not have any rows or skipped invalid input lines
    lines = result.split('\n')
    assert len(lines) == 2
