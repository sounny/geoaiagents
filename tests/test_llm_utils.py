import pytest
from unittest.mock import MagicMock
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_first_success():
    client = MagicMock()
    expected_response = MagicMock()
    expected_response.choices = ["choice1"]
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, max_retries=3, model='x')

    assert response is expected_response
    assert client.chat.completions.create.call_count == 1

def test_call_llm_with_retry_succeeds_after_one_failure(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)
    client = MagicMock()
    expected_response = MagicMock()
    expected_response.choices = ["choice1"]

    client.chat.completions.create.side_effect = [TimeoutError("timeout"), expected_response]

    response = call_llm_with_retry(client, max_retries=3, model='x')

    assert response is expected_response
    assert client.chat.completions.create.call_count == 2

def test_call_llm_with_retry_always_fails_with_timeout(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)
    client = MagicMock()
    client.chat.completions.create.side_effect = TimeoutError("timeout")

    with pytest.raises(ValueError) as excinfo:
        call_llm_with_retry(client, max_retries=2, model='x')

    assert "failed after 2 attempts" in str(excinfo.value)
    assert client.chat.completions.create.call_count == 2
