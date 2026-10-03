import pytest
from webchat import create_map_html

def test_create_map_html_multiple_points():
    points = [(48.8, 2.3), (-33.9, 151.2)]
    html = create_map_html(points)
    assert isinstance(html, str)
    assert len(html) > 0
    assert '48.8' in html
    assert '2.3' in html
    assert '-33.9' in html
    assert '151.2' in html

def test_create_map_html_empty():
    points = []
    html = create_map_html(points)
    assert html == ""
