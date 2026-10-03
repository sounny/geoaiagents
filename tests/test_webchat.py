import pytest
import webchat
from webchat import create_map_html

def test_create_map_html_empty_list():
    assert create_map_html([]) == ""

def test_create_map_html_three_points_distinct(monkeypatch):
    class MockMap:
        def __init__(self, *args, **kwargs):
            self.content = "html:"
        def _repr_html_(self):
            return self.content

    class MockMarker:
        def __init__(self, location, *args, **kwargs):
            self.location = location
        def add_to(self, m):
            m.content += f" {self.location[0]},{self.location[1]}"

    monkeypatch.setattr(webchat.folium, "Map", MockMap)
    monkeypatch.setattr(webchat.folium, "Marker", MockMarker)

    html = create_map_html([(48.8, 2.3), (-33.9, 151.2), (40.7, -74.0)])
    assert html != ""
    assert "48.8" in html
    assert "2.3" in html
    assert "-33.9" in html
    assert "151.2" in html
    assert "40.7" in html
    assert "-74" in html
