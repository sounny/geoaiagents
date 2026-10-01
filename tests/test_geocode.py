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

def test_reverse_geocode_invalid_inputs():
    result = reverse_geocode_coordinates("abc, def; 100, 200")
    assert "_Skipped invalid inputs:_" in result
    assert "abc, def" in result
    assert "100, 200" in result

def test_parse_locations_drop_empty_tokens(mocker):
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("Should not geocode"))
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("Should not reverse geocode"))
    from geocode import parse_locations

    assert parse_locations('Paris;') == ['Paris']
    assert parse_locations(';Lyon;') == ['Lyon']
    assert parse_locations('') == []
    assert parse_locations('A\n\nB') == ['A', 'B']
