import pytest
import os
import sys

# Ensure root directory is in sys.path if not already, to allow importing webchat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webchat import create_map_html

def test_create_map_html_empty():
    html = create_map_html([])
    assert html == '<div style="padding: 20px; text-align: center; color: gray;">No map data available.</div>'

def test_create_map_html_with_points():
    html = create_map_html([(10.0, 20.0)])
    assert "leaflet" in html.lower()

if __name__ == '__main__':
    pytest.main(['-v', __file__])
