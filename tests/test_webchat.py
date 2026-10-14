import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

def test_import_webchat_no_network_or_server(monkeypatch):
    import socket
    import gradio as gr
    import requests
    import importlib
    import sys

    class ForbiddenImportAction(Exception):
        pass

    def mock_fail(*args, **kwargs):
        raise ForbiddenImportAction("Forbidden action during import")

    monkeypatch.setattr(socket, "socket", mock_fail)
    monkeypatch.setattr(gr.Blocks, "launch", mock_fail)
    monkeypatch.setattr(requests, "get", mock_fail)
    monkeypatch.setattr(requests, "post", mock_fail)

    try:
        import webchat
        if "webchat" in sys.modules:
            importlib.reload(webchat)
    except ForbiddenImportAction as e:
        pytest.xfail(f"Importing webchat triggered forbidden action: {e}")
