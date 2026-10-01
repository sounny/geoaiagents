import pytest
from unittest.mock import MagicMock
import time
from llm_utils import call_llm_with_retry

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

def test_call_llm_with_retry_immediate_success(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda x: None)
    client = MagicMock()
    mock_response = MockResponse(choices=[{'ok': True}])
    client.chat.completions.create.return_value = mock_response

    response = call_llm_with_retry(client, model='m', messages=[])
    assert response == mock_response
    assert client.chat.completions.create.call_count == 1

def test_call_llm_with_retry_one_failure(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda x: None)
    client = MagicMock()
    mock_response = MockResponse(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError("timeout"), mock_response]

    response = call_llm_with_retry(client, model='m', messages=[])
    assert response == mock_response
    assert client.chat.completions.create.call_count == 2

def test_call_llm_with_retry_exhaustion(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda x: None)
    client = MagicMock()
    client.chat.completions.create.side_effect = TimeoutError("timeout")

    with pytest.raises(ValueError) as exc:
        call_llm_with_retry(client, max_retries=2, model='m', messages=[])

    assert "failed after 2 attempts" in str(exc.value)
    assert client.chat.completions.create.call_count == 2
