import pytest
from unittest.mock import MagicMock
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_happy_path():
    client = MagicMock()
    success_response = MagicMock()
    success_response.choices = [object()]
    client.chat.completions.create.return_value = success_response

    response = call_llm_with_retry(client, max_retries=3, model='x')

    assert response == success_response
    client.chat.completions.create.assert_called_once_with(model='x')

def test_call_llm_with_retry_timeout_then_success(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

    client = MagicMock()
    success_response = MagicMock()
    success_response.choices = [object()]

    client.chat.completions.create.side_effect = [
        TimeoutError("Connection timed out"),
        success_response
    ]

    response = call_llm_with_retry(client, max_retries=3, model='x')

    assert response == success_response
    assert client.chat.completions.create.call_count == 2
