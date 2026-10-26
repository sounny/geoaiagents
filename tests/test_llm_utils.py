import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(monkeypatch):
    monkeypatch.setattr('time.sleep', MagicMock())
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="ok")])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2
from collections import OrderedDict

class MyStr(str): pass
class MyInt(int): pass
class MyDict(dict): pass
class MyList(list): pass

@pytest.mark.xfail(raises=AssertionError, reason="Types are not coerced to plain builtins")
def test_call_llm_with_retry_subclass_types():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message="hi")]
    )

    my_str = MyStr("m")
    my_int = MyInt(3)
    my_dict = MyDict({"role": MyStr("user")})
    my_list = MyList([my_dict])

    call_llm_with_retry(client, max_retries=my_int, model=my_str, messages=my_list)

    actual_kwargs = client.chat.completions.create.call_args[1]

    assert type(actual_kwargs["model"]) is str
    assert type(actual_kwargs["messages"]) is list
    assert type(actual_kwargs["messages"][0]) is dict
    assert type(actual_kwargs["messages"][0]["role"]) is str

@pytest.mark.xfail(raises=AssertionError, reason="OrderedDict is not coerced to plain dict")
def test_call_llm_with_retry_ordereddict():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message="hi")]
    )

    ordered_dict = OrderedDict({"role": "user"})

    call_llm_with_retry(client, max_retries=3, model="m", messages=[ordered_dict])

    actual_kwargs = client.chat.completions.create.call_args[1]

    assert type(actual_kwargs["messages"][0]) is dict
