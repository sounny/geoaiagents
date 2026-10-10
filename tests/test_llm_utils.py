from unittest.mock import MagicMock, patch
from llm_utils import call_llm_with_retry

class MockResponse(dict):
    @property
    def choices(self):
        return ["choice"]

@patch("time.sleep")
def test_call_llm_retry_once_success(mock_sleep):
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        Exception("error"),
        MockResponse({"ok": True})
    ]
    response = call_llm_with_retry(client, max_retries=3)
    assert response == {"ok": True}
    assert client.chat.completions.create.call_count == 2
