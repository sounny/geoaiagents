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

@pytest.mark.xfail(raises=ValueError, strict=True, reason="Bug: Retries on TypeError/AttributeError instead of failing immediately and wraps in ValueError")
def test_call_llm_with_retry_wrong_client_type():
    call_llm_with_retry("not a client", max_retries=1)

def test_call_llm_with_retry_wrong_max_retries_type():
    client = MagicMock()
    with pytest.raises(TypeError):
        call_llm_with_retry(client, max_retries="3")
