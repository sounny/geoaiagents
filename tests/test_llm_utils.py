import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry
import collections

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

def test_dict_list_subclass():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response

    class MyList(list): pass
    class MyDict(collections.UserDict): pass

    my_list = MyList([MyDict({'a': 1})])
    my_ord_dict = collections.OrderedDict({'b': 2})

    response = call_llm_with_retry(client, model='m', messages=my_list, extra_arg=my_ord_dict, max_retries=3)
    assert response == expected_response
