import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry
import copy
import inspect

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = copy.deepcopy(expected_response)

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.side_effect = [TimeoutError('t'), copy.deepcopy(expected_response)]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_public_functions_idempotency(mocker, tmp_path):
    import llm_utils
    # Mock external calls, network, and filesystem
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open())

    # We use tmp_path to mock filesystem just to satisfy the requirement
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    public_funcs = [obj for name, obj in inspect.getmembers(llm_utils) if callable(obj) and getattr(obj, '__module__', '') == llm_utils.__name__ and not name.startswith('_')]

    for func in public_funcs:
        # We need to construct arguments for the function dynamically
        sig = inspect.signature(func)
        args = []
        kwargs = {}

        # Setup specific mock for the client
        client_mock = MagicMock()
        mock_response = SimpleNamespace(choices=[SimpleNamespace(message={"ok": True})])
        client_mock.chat.completions.create.return_value = copy.deepcopy(mock_response)

        for name, param in sig.parameters.items():
            if param.default != inspect.Parameter.empty:
                kwargs[name] = param.default
            elif name == 'client':
                args.append(client_mock)
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                kwargs['model'] = 'm'
                kwargs['messages'] = []
            else:
                args.append(MagicMock())

        # First call
        response1 = func(*args, **kwargs)

        # Keep a deep copy to represent the "unchanged" state
        original_response_copy = copy.deepcopy(response1)

        # Mutate any list or dict returned by the first call
        if isinstance(response1, list):
            response1.append("mutated")
        elif isinstance(response1, dict):
            response1["mutated"] = True
        elif hasattr(response1, 'choices') and isinstance(response1.choices, list):
            response1.choices.append("mutated")

        # Reset specific mocks if needed for second call
        client_mock.chat.completions.create.return_value = copy.deepcopy(mock_response)

        # Second call
        response2 = func(*args, **kwargs)

        # Assert the second call result is unchanged relative to the original first call
        assert response2 == original_response_copy
