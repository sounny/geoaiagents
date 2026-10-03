import pytest
from unittest.mock import patch, Mock
import requests
from file_loaders import fetch_geo_boundaries

def test_fetch_geo_boundaries_second_get_exception():
    with patch('file_loaders.requests.get') as mock_get:
        mock_response_1 = Mock()
        mock_response_1.json.return_value = {"simplifiedGeometryGeoJSON": "http://example.com/geo.json"}
        mock_response_1.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_1, requests.RequestException("Network error")]

        result = fetch_geo_boundaries("USA")

        assert result == "| Latitude | Longitude |\n|---------:|----------:|"
