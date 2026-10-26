import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda x: None)
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(reason="Silently passes empty model string to LLM client instead of raising ValueError")
def test_call_llm_with_retry_model_empty_string():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response
    with pytest.raises(ValueError):
        call_llm_with_retry(client, model="", messages=[], max_retries=1)


@pytest.mark.xfail(reason="Silently passes whitespace model string to LLM client instead of raising ValueError")
def test_call_llm_with_retry_model_whitespace_string():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response
    with pytest.raises(ValueError):
        call_llm_with_retry(client, model="   ", messages=[], max_retries=1)
