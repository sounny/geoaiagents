import pytest
from unittest.mock import patch
import geocode

print("Let's mock geocode_limiter directly to check if it's swallowing exceptions natively")
try:
    with patch("geocode._geocode_limiter", side_effect=Exception("Timeout Error from Limiter")) as mock_conn:
        res = geocode.get_coordinates("Paris", timeout=10**100)
        print("Result:", res)
except Exception as e:
    print(type(e), e)
