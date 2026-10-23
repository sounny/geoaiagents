import copy
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_call_llm_with_retry_mutability():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response

    messages = [{"role": "user", "content": "hello"}]
    tools = [{"type": "function", "function": {"name": "test"}}]

    messages_copy = copy.deepcopy(messages)
    tools_copy = copy.deepcopy(tools)

    call_llm_with_retry(client, max_retries=1, messages=messages, tools=tools)

    assert messages == messages_copy, "Caller's 'messages' argument was mutated"
    assert tools == tools_copy, "Caller's 'tools' argument was mutated"
