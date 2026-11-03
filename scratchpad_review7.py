import pytest
from unittest.mock import patch
import geocode

print("Testing direct mocked HTTP calls catching")
try:
    with patch("geopy.adapters.URLLibAdapter.get_text", side_effect=Exception("Simulated HTTP Timeout")) as mock_conn:
        geocode.get_coordinates("Paris", timeout=10**100)
        mock_conn.assert_called_with('https://nominatim.openstreetmap.org/search?q=Paris&format=json&limit=1&accept-language=en', timeout=10**100, headers={'User-Agent': 'my_geocoder_app'})
        print("Success get_coordinates 10**100")
except Exception as e:
    print(type(e), e)
