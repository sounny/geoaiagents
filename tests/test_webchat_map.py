import os
import sys
import pytest
from unittest.mock import MagicMock

# Ensure root directory is in sys.path if not already, to allow importing webchat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import webchat

def test_infer_location_with_for():
    assert webchat.infer_location("Map for Paris") == "Paris"
    assert webchat.infer_location("Find something for New York, NY") == "New York, NY"
    assert webchat.infer_location("for London") == "London"
    assert webchat.infer_location("Show map for San Francisco") == "San Francisco"

def test_infer_location_without_for():
    assert webchat.infer_location("Map of Paris") is None
    assert webchat.infer_location("Hello world") is None
    assert webchat.infer_location("") is None

def test_create_map_html_empty_points():
    assert webchat.create_map_html([]) == ""

def test_create_map_html_non_empty_points(mocker):
    mock_map_instance = MagicMock()
    mock_map_instance._repr_html_.return_value = "<div>Mocked Map</div>"
    mock_folium_map = mocker.patch("webchat.folium.Map", return_value=mock_map_instance)

    mock_marker_instance = MagicMock()
    mock_folium_marker = mocker.patch("webchat.folium.Marker", return_value=mock_marker_instance)

    points = [(48.8566, 2.3522), (51.5074, -0.1278)]
    html = webchat.create_map_html(points)

    assert html == "<div>Mocked Map</div>"
    mock_folium_map.assert_called_once_with(location=(48.8566, 2.3522), zoom_start=4)
    assert mock_folium_marker.call_count == 2
    mock_folium_marker.assert_any_call([48.8566, 2.3522])
    mock_folium_marker.assert_any_call([51.5074, -0.1278])
    assert mock_marker_instance.add_to.call_count == 2
    mock_marker_instance.add_to.assert_called_with(mock_map_instance)
