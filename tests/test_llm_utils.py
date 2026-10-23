import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

def test_llm_utils_signatures():
    import inspect
    import llm_utils

    sig = inspect.signature(llm_utils.call_llm_with_retry)

    assert 'client' in sig.parameters
    assert sig.parameters['client'].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert sig.parameters['client'].default == inspect.Parameter.empty

    assert 'max_retries' in sig.parameters
    assert sig.parameters['max_retries'].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert sig.parameters['max_retries'].default == 3

    assert 'kwargs' in sig.parameters
    assert sig.parameters['kwargs'].kind == inspect.Parameter.VAR_KEYWORD
    assert sig.parameters['kwargs'].default == inspect.Parameter.empty

    assert list(sig.parameters.keys()) == ['client', 'max_retries', 'kwargs']
