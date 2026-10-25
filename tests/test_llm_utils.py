import warnings
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda x: None)
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

def test_public_functions_no_warnings():
    import inspect
    import llm_utils
    public_functions = [
        (name, func) for name, func in inspect.getmembers(llm_utils, inspect.isfunction)
        if not name.startswith('_') and getattr(func, '__module__', '') == llm_utils.__name__
    ]

    for name, func in public_functions:
        if name == 'call_llm_with_retry':
            pass # already tested manually
        else:
            pytest.fail(f"Unhandled public function: {name}")
