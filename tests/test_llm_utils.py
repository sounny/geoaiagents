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


def test_call_llm_with_retry_large_inputs():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    long_string = "a" * 1000000
    large_list = [{"role": "user", "content": "b"}] * 10000
    big_dict = {f"key_{i}": "value" for i in range(10000)}

    import time
    start = time.time()
    response = call_llm_with_retry(
        client,
        model=long_string,
        messages=large_list,
        tools=big_dict,
        max_retries=3
    )
    end = time.time()

    assert response == expected_response
    assert end - start < 5.0
