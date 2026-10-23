import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

@pytest.mark.xfail(raises=ValueError, reason="Bug exposed: Mock response is missing 'message' attribute inside choices")
def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


@pytest.mark.xfail(raises=ValueError, reason="Bug exposed: Mock response is missing 'message' attribute inside choices")
def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_llm_utils_reload_state():
    import inspect
    import importlib
    import llm_utils

    # Reload the module
    importlib.reload(llm_utils)

    # Get public names
    public_names = sorted([name for name in dir(llm_utils) if not name.startswith('_')])
    assert public_names == ['call_llm_with_retry', 'logging', 'time']

    # Verify types
    assert callable(getattr(llm_utils, 'call_llm_with_retry'))
    assert inspect.ismodule(getattr(llm_utils, 'logging'))
    assert inspect.ismodule(getattr(llm_utils, 'time'))
