import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_call_llm_with_retry_client_none():
    with pytest.raises(ValueError, match="LLM call failed after 3 attempts"):
        call_llm_with_retry(None, model='m', messages=[], max_retries=3)


def test_call_llm_with_retry_max_retries_zero():
    client = MagicMock()
    with pytest.raises(ValueError, match="LLM call failed after 0 attempts"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=0)


def test_call_llm_with_retry_max_retries_negative():
    client = MagicMock()
    with pytest.raises(ValueError, match="LLM call failed after -1 attempts"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=-1)


def test_call_llm_with_retry_max_retries_none():
    client = MagicMock()
    with pytest.raises(TypeError, match="'NoneType' object cannot be interpreted as an integer"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=None)


def test_call_llm_with_retry_missing_choices():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace()
    with pytest.raises(ValueError, match="LLM call failed after 1 attempts.*'choices' missing or empty"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=1)


def test_call_llm_with_retry_empty_choices():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[])
    with pytest.raises(ValueError, match="LLM call failed after 1 attempts.*'choices' missing or empty"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=1)


def test_call_llm_with_retry_missing_message():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace()])
    with pytest.raises(ValueError, match="LLM call failed after 1 attempts.*'message' missing or empty in first choice"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=1)


def test_call_llm_with_retry_empty_message():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message="")])
    with pytest.raises(ValueError, match="LLM call failed after 1 attempts.*'message' missing or empty in first choice"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=1)
