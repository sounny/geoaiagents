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


def test_llm_utils_public_names():
    import llm_utils
    import inspect

    public_names = []
    for name in dir(llm_utils):
        if not name.startswith('_'):
            obj = getattr(llm_utils, name)
            if inspect.isclass(obj):
                kind = 'class'
            elif inspect.isfunction(obj):
                kind = 'function'
            elif inspect.ismodule(obj):
                kind = 'module'
            else:
                kind = 'constant'
            public_names.append((name, kind))

    public_names.sort()
    expected = [
        ('call_llm_with_retry', 'function'),
        ('logging', 'module'),
        ('time', 'module')
    ]
    assert public_names == expected
