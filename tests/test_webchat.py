import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

from unittest.mock import patch, MagicMock
from webchat import respond, messages

@pytest.mark.xfail(reason="Webchat does not truncate or reject large messages")
@patch("webchat.call_llm_with_retry")
def test_large_message_handling_locking_length_limit(mock_call):
    messages.clear()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Processed"
    mock_call.return_value = mock_response

    long_msg = "A" * 20000

    reply, map_html, logs, table = respond(long_msg, [], None)

    # We want to check if the large message was truncated in the messages sent to the LLM.
    # The global messages list is passed by reference, so we inspect it directly.
    # Find the user's message we just added
    user_msgs = [m for m in messages if m.get("role") == "user"]
    last_user_content = str(user_msgs[-1].get("content", ""))

    assert len(last_user_content) < 20000
