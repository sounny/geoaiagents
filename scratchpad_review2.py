import pytest
from unittest.mock import patch
import geocode

print("Let's mock URLLibAdapter.get_text to throw an error and see what exceptions geocode.py raises")
try:
    with patch("geopy.adapters.URLLibAdapter.get_text", side_effect=Exception("Simulated HTTP timeout/error")) as mock_conn:
        res = geocode.get_coordinates("Paris", timeout=10**100)
        print("Result:", res)
except Exception as e:
    print(type(e), e)
