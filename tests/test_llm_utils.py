import sys
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="test"))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="test"))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_call_llm_with_retry_zero_retries():
    client = MagicMock()
    with pytest.raises(ValueError, match="LLM call failed after 0 attempts"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=0)


def test_call_llm_with_retry_negative_retries():
    client = MagicMock()
    with pytest.raises(ValueError, match="LLM call failed after -1 attempts"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=-1)


def test_call_llm_with_retry_nan_retries():
    client = MagicMock()
    with pytest.raises(TypeError, match="'float' object cannot be interpreted as an integer"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=float('nan'))


def test_call_llm_with_retry_inf_retries():
    client = MagicMock()
    with pytest.raises(TypeError, match="'float' object cannot be interpreted as an integer"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=float('inf'))


def test_call_llm_with_retry_maxsize_retries():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="test"))])
    client.chat.completions.create.return_value = expected_response
    response = call_llm_with_retry(client, model='m', messages=[], max_retries=sys.maxsize)
    assert response == expected_response
    client.chat.completions.create.assert_called_once()
