import pytest
from unittest.mock import MagicMock, patch
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_one_retry_happy_path():
    client = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [{"ok": True}]

    client.chat.completions.create.side_effect = [
        Exception("Temporary failure"),
        mock_response
    ]

    with patch("time.sleep") as mock_sleep:
        result = call_llm_with_retry(client, max_retries=3, model="gpt-4")

    assert result == mock_response
    assert client.chat.completions.create.call_count == 2
    mock_sleep.assert_called_once_with(1)
