from webchat import create_map_html

def test_create_map_html_single_point():
    html = create_map_html([(48.8566, 2.3522)])
    assert isinstance(html, str)
    assert html != ""
    assert "48.8566" in html
    assert "2.3522" in html

def test_create_map_html_empty_list():
    assert create_map_html([]) == ""
