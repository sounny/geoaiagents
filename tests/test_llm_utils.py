import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="café 안녕하세요 🚀")])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[{'role': 'user', 'content': 'café 안녕하세요 🚀'}], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once_with(model='m', messages=[{'role': 'user', 'content': 'café 안녕하세요 🚀'}])


@patch('time.sleep')
def test_call_llm_with_retry_timeout_then_success(mock_sleep):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="café 안녕하세요 🚀")])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[{'role': 'user', 'content': 'café 안녕하세요 🚀'}], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2
