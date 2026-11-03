import pytest
from unittest.mock import patch
import geocode

print("Let's check if the Exception catches it")
try:
    with patch("socket.create_connection") as mock_conn:
        geocode.get_coordinates("Paris", timeout=10**100)
except Exception as e:
    print(type(e))
