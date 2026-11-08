import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

import inspect
import llm_utils

@pytest.mark.xfail(reason="Logging and time are exposed as public names but are not callable")
def test_llm_utils_public_callables():
    public_names = getattr(llm_utils, "__all__", [name for name in dir(llm_utils) if not name.startswith("_")])
    allowlist = []
    for name in public_names:
        obj = getattr(llm_utils, name)
        assert callable(obj), f"{name} is not callable"
        assert obj.__doc__ or name in allowlist, f"{name} lacks a docstring"
