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

def test_call_llm_with_retry_timeout_then_success(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda x: None)
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(raises=AssertionError, reason="Strict equivalence fails as iterator is not converted to list (bug for retries)", strict=True)
def test_call_llm_with_retry_list_vs_iter():
    client_list = MagicMock()
    client_iter = MagicMock()

    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client_list.chat.completions.create.return_value = expected_response
    client_iter.chat.completions.create.return_value = expected_response

    list_msgs = [{'role': 'user'}]
    iter_msgs = iter([{'role': 'user'}])

    res_list = call_llm_with_retry(client_list, messages=list_msgs)
    res_iter = call_llm_with_retry(client_iter, messages=iter_msgs)

    assert res_list == res_iter

    assert client_list.chat.completions.create.call_args == client_iter.chat.completions.create.call_args
