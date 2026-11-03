import pytest
from unittest.mock import patch
import geocode

print("Let's assert that the mocked function was actually called with the correct timeout")
try:
    with patch("geopy.adapters.URLLibAdapter.get_text", side_effect=Exception("Simulated error")) as mock_conn:
        res = geocode.get_coordinates("Paris", timeout=10**100)
        print("Result:", res)
        mock_conn.assert_called()
        print("Called with:", mock_conn.call_args)
except Exception as e:
    print(type(e), e)
