import pytest
import requests
from file_loaders import fetch_geo_boundaries, _table

def test_fetch_geo_boundaries_blank_iso(mocker):
    mock_get = mocker.patch("requests.get")
    result = fetch_geo_boundaries("   ")
    assert result == _table([])
    mock_get.assert_not_called()

def test_fetch_geo_boundaries_empty_iso(mocker):
    mock_get = mocker.patch("requests.get")
    result = fetch_geo_boundaries("")
    assert result == _table([])
    mock_get.assert_not_called()
