import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webchat import create_map_html

def test_create_map_html_with_points():
    points = [(48.8566, 2.3522)]
    html = create_map_html(points)

    assert html is not None
    assert isinstance(html, str)
    assert len(html.strip()) > 0

    html_lower = html.lower()
    assert "folium" in html_lower or "leaflet" in html_lower
