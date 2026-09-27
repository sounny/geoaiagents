import pytest
from geocode import get_coordinates, reverse_geocode_coordinates
import geocode

def test_get_coordinates_timeout_override(mocker):
    mock_geocode_rl = mocker.patch("geocode._geocode_rl")

    get_coordinates("Test City", timeout=5)

    # Assert _geocode_rl was called with timeout=5
    mock_geocode_rl.assert_called_with(
        "Test City",
        language="en",
        viewbox=None,
        bounded=False,
        timeout=5,
    )

def test_reverse_geocode_coordinates_timeout_override(mocker):
    mock_reverse_rl = mocker.patch("geocode._reverse_rl")
    # Also need to mock geocode.Nominatim just in case, but we patch _reverse_rl directly

    reverse_geocode_coordinates("12.34, 56.78", timeout=10)

    # Assert _reverse_rl was called with timeout=10
    mock_reverse_rl.assert_called_with(
        (12.34, 56.78),
        language="en",
        timeout=10,
    )
