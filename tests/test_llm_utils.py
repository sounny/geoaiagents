import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
import copy
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success(tmp_path):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()
    assert response == copy.deepcopy(response)


@patch('time.sleep')
def test_call_llm_with_retry_timeout_then_success(mock_sleep, tmp_path):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2
    assert response == copy.deepcopy(response)
