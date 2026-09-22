import pytest
from unittest.mock import patch, MagicMock
from geocode import parse_locations, geocode_locations, reverse_geocode_coordinates

def test_parse_locations():
    assert parse_locations("Austin, TX; Paris, France\nLondon") == ["Austin, TX", "Paris, France", "London"]
    assert parse_locations("   foo  ; bar\n") == ["foo", "bar"]

@patch('geocode.get_coordinates')
def test_geocode_locations(mock_get_coordinates):
    # Mocking get_coordinates to return a dummy response
    mock_get_coordinates.side_effect = [
        ("Austin, Texas, United States", 30.2711, -97.7437),
        (None, None, None)
    ]

    res = geocode_locations("Austin, TX; UnknownPlace")
    assert "Austin, Texas, United States" in res
    assert "30.2711" in res
    assert "UnknownPlace" in res
    assert "Not found" in res

@patch('geocode.RateLimiter')
@patch('geocode.Nominatim')
def test_reverse_geocode_coordinates(mock_nominatim, mock_ratelimiter):
    # Setup mock
    mock_location = MagicMock()
    mock_location.address = "123 Main St, Springfield"

    mock_reverse = MagicMock()
    mock_reverse.side_effect = [
        mock_location,
        Exception("Geocoding failed")
    ]

    mock_ratelimiter.return_value = mock_reverse

    res = reverse_geocode_coordinates("39.78,-89.65; 0,0")

    assert "123 Main St, Springfield" in res
    assert "Not found" in res
