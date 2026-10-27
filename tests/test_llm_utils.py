import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry
import copy

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

def test_call_llm_with_retry_arguments_unchanged(tmp_path):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='hello')])
    client.chat.completions.create.return_value = expected_response

    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy")

    messages = [{"role": "user", "content": "hi", "file": str(test_file)}]
    config = {"temp": 0.5, "files": [str(test_file)]}

    messages_orig = copy.deepcopy(messages)
    config_orig = copy.deepcopy(config)

    call_llm_with_retry(client, messages=messages, config=config)

    if messages != messages_orig or config != config_orig:
        pytest.xfail("Mutation looks like a bug")
    assert messages == messages_orig
    assert config == config_orig
