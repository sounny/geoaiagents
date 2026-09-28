import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations

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

def test_parse_locations():
    # Single location
    assert parse_locations("New York") == ["New York"]

    # Newline separated
    assert parse_locations("New York\nLondon\nParis") == ["New York", "London", "Paris"]

    # Semicolon separated
    assert parse_locations("New York;London;Paris") == ["New York", "London", "Paris"]

    # Mixed delimiters with extra whitespace
    assert parse_locations(" New York ; London \n Paris ;   Tokyo  ") == ["New York", "London", "Paris", "Tokyo"]

    # Empty and whitespace-only strings
    assert parse_locations("") == []
    assert parse_locations("   ") == []
    assert parse_locations(" \n ; \n ") == []
