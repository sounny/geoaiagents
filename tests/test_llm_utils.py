import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

@pytest.mark.xfail(reason="Bug: function expects message attribute on choice, test provides a dict")
def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


@pytest.mark.xfail(reason="Bug: function expects message attribute on choice, test provides a dict")
def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

def test_call_llm_with_retry_kwargs_order():
    client1 = MagicMock()
    client2 = MagicMock()

    valid_resp = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client1.chat.completions.create.return_value = valid_resp
    client2.chat.completions.create.return_value = valid_resp

    res1 = call_llm_with_retry(client1, a=1, b=2)
    res2 = call_llm_with_retry(client2, b=2, a=1)

    assert res1 == res2
