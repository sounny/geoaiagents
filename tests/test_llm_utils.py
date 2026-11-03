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

@patch('time.sleep')
def test_call_llm_with_retry_timeout_then_success(mock_sleep):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(raises=StopIteration, reason="Large ints cause unrealistic loop counts/hangs on failure")
@patch('time.sleep')
def test_call_llm_with_retry_large_int(mock_sleep):
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("network failure")

    mock_sleep.side_effect = StopIteration("Broken loop")

    call_llm_with_retry(client, model='m', messages=[], max_retries=10**100)

@pytest.mark.xfail(raises=RuntimeError, reason="Passing bool True is treated as 1, False as 0 which is a bug for retry counts")
@patch('time.sleep')
def test_call_llm_with_retry_bool_true(mock_sleep):
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("network failure")

    call_llm_with_retry(client, model='m', messages=[], max_retries=True)

@pytest.mark.xfail(raises=ValueError, reason="Passing bool False is treated as 0 and immediately fails")
def test_call_llm_with_retry_bool_false():
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("network failure")

    call_llm_with_retry(client, model='m', messages=[], max_retries=False)
