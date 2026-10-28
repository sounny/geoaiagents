import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    # The actual code expects 'message' property on the first choice
    message = SimpleNamespace(content="test")
    choice = SimpleNamespace(message=message)
    expected_response = SimpleNamespace(choices=[choice])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()

def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    message = SimpleNamespace(content="test")
    choice = SimpleNamespace(message=message)
    expected_response = SimpleNamespace(choices=[choice])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

def test_llm_utils_env_vars_skipped(monkeypatch):
    '''
    Test environment variables for llm_utils.py
    Since the module does not read any environment variables, this is an empty test with skip.
    '''
    pytest.skip("llm_utils.py does not read any environment variables")
