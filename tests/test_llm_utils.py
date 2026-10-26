import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

class MockMessage:
    def __init__(self, content):
        self.content = content
    def __bool__(self):
        return bool(self.content)

class MockChoice:
    def __init__(self, message):
        self.message = message


def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[MockChoice(MockMessage("ok"))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[MockChoice(MockMessage("ok"))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(reason="Tuple and list do not result in same kwargs passed to create")
def test_call_llm_with_retry_sequence_equivalency():
    client1 = MagicMock()
    client2 = MagicMock()

    expected_response = SimpleNamespace(choices=[MockChoice(MockMessage("ok"))])
    client1.chat.completions.create.return_value = expected_response
    client2.chat.completions.create.return_value = expected_response

    list_arg = [{'role': 'user', 'content': 'test'}]
    tuple_arg = ({'role': 'user', 'content': 'test'},)

    res1 = call_llm_with_retry(client1, messages=list_arg)
    res2 = call_llm_with_retry(client2, messages=tuple_arg)

    assert res1 == res2
    assert client1.chat.completions.create.call_args == client2.chat.completions.create.call_args
