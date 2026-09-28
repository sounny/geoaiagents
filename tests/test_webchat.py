import sys
import webchat
from unittest.mock import patch

def test_chat_empty_message():
    history = []
    message = "   "
    upload_file = None

    with patch("webchat.call_llm_with_retry") as mock_call_llm:
        new_history, map_html, logs, table = webchat.chat(message, history, upload_file)

        # Verify LLM was not called
        mock_call_llm.assert_not_called()

        # Verify the returned history only contains the user's message
        assert len(new_history) == 2
        assert new_history[-2]["content"] == "   "
        assert new_history[-1]["content"] == ""
