import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()

def test_call_llm_with_retry_timeout_then_success():
    with patch('time.sleep'):
        client = MagicMock()
        expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
        client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

        response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

        assert response == expected_response
        assert client.chat.completions.create.call_count == 2

def test_call_llm_with_retry_unknown_kwargs():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3, unknown_key='value')

    assert response == expected_response
    client.chat.completions.create.assert_called_once_with(model='m', messages=[], unknown_key='value')

    # Behavior looks like a bug: unknown config keys should be validated or rejected, but are passed directly to client
    pytest.xfail("Silently passes unknown kwargs to the LLM client without validation")
