import pytest
from unittest.mock import patch
from webchat import parse_distance_table, chat

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

@pytest.mark.xfail(reason="User message is not HTML-escaped before being returned in history")
@patch('webchat.respond')
def test_chat_html_escapes_user_message(mock_respond):
    mock_respond.return_value = ("response", "map", "logs", "table")
    malicious_input = "<script>alert('xss')</script>"
    history, map_html, logs, table = chat(malicious_input, [], None)

    user_msg_content = history[-2]["content"]
    assert "<script>" not in user_msg_content
    assert "&lt;script&gt;" in user_msg_content
