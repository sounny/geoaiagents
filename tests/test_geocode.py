import pytest
from geocode import get_coordinates, reverse_geocode_coordinates

def test_get_coordinates_timeout_or_error(mocker):
    # Mock _geocode_limiter to raise an exception
    mocker.patch("geocode._geocode_limiter", side_effect=Exception("Mocked timeout"))
    result = get_coordinates("Some location")
    assert result == (None, None, None)

def test_reverse_geocode_timeout_or_error(mocker):
    mocker.patch("geocode._reverse_limiter", side_effect=Exception("Mocked timeout"))
    result = reverse_geocode_coordinates("40.0, -70.0")
    assert "| 40.0 | -70.0 | Not found |" in result

def test_reverse_geocode_invalid_inputs(mocker):
    # Mock to ensure network is not called when all inputs are invalid
    mock_limiter = mocker.patch("geocode._reverse_limiter")

    result = reverse_geocode_coordinates("not-a-pair; abc, def; 100, 200")

    assert "Error: No valid coordinate pairs provided." in result
    assert "_Skipped invalid inputs:_" in result
    assert "not-a-pair" in result
    assert "abc, def" in result
    assert "100, 200" in result

    # Assert network was not called
    mock_limiter.assert_not_called()
