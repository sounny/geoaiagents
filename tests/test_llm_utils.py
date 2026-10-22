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


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_call_llm_with_retry_missing_choices(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace()
    client.chat.completions.create.return_value = expected_response

    with pytest.raises(ValueError) as excinfo:
        call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert "LLM call failed after 3 attempts: Malformed response: 'choices' missing or empty" in str(excinfo.value)
    assert client.chat.completions.create.call_count == 3


def test_call_llm_with_retry_missing_message(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace()])
    client.chat.completions.create.return_value = expected_response

    with pytest.raises(ValueError) as excinfo:
        call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert "LLM call failed after 3 attempts: Malformed response: 'message' missing or empty in first choice" in str(excinfo.value)
    assert client.chat.completions.create.call_count == 3


def test_call_llm_with_retry_max_retries_exceeded_with_timeout(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    client.chat.completions.create.side_effect = TimeoutError('t')

    with pytest.raises(ValueError) as excinfo:
        call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert "LLM call failed after 3 attempts: t" in str(excinfo.value)
    assert client.chat.completions.create.call_count == 3


def test_call_llm_with_retry_zero_retries():
    client = MagicMock()

    with pytest.raises(ValueError) as excinfo:
        call_llm_with_retry(client, model='m', messages=[], max_retries=0)

    assert "LLM call failed after 0 attempts" in str(excinfo.value)
    assert client.chat.completions.create.call_count == 0
