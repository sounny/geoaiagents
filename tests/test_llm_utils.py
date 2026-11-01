import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(reason="looks like a bug: fails to validate that messages is an ordered sequence, allowing sets")
def test_call_llm_with_retry_messages_set():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.return_value = expected_response

    with pytest.raises((TypeError, ValueError)):
        call_llm_with_retry(client, model="m", messages=set(), max_retries=1)

@pytest.mark.xfail(reason="looks like a bug: fails to validate that messages is an ordered sequence, allowing frozensets")
def test_call_llm_with_retry_messages_frozenset():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.return_value = expected_response

    with pytest.raises((TypeError, ValueError)):
        call_llm_with_retry(client, model="m", messages=frozenset(), max_retries=1)
