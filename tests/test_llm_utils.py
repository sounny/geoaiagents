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

@pytest.mark.parametrize('text_input', [
    'test string',
    pytest.param(b'test string', marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: fails to coerce bytes to string before passing to client"))
])
def test_call_llm_with_retry_bytes(text_input):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model=text_input, messages=[{'role': 'user', 'content': text_input}], max_retries=3)

    assert response == expected_response

    call_kwargs = client.chat.completions.create.call_args[1]
    assert type(call_kwargs['model']) is str
    assert type(call_kwargs['messages'][0]['content']) is str
    assert call_kwargs['model'] == 'test string'
    assert call_kwargs['messages'][0]['content'] == 'test string'
