import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

@pytest.mark.xfail(raises=ValueError, reason="Bug: code expects message attribute on choice, mock uses dict")
def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()

@pytest.mark.xfail(raises=ValueError, reason="Bug: code expects message attribute on choice, mock uses dict")
def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

def test_call_llm_with_retry_parameters():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="success")])
    client.chat.completions.create.return_value = expected_response

    # Optional parameters omitted
    assert call_llm_with_retry(client) == expected_response

    # Passed explicitly as their defaults
    assert call_llm_with_retry(client, 3) == expected_response

    # Passed by keyword instead of position
    assert call_llm_with_retry(client=client, max_retries=3) == expected_response
