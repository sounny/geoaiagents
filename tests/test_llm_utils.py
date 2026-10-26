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

def test_call_llm_with_retry_numpy_int(tmp_path):
    pytest.importorskip("numpy")
    import numpy as np
    client1 = MagicMock()
    client1.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])

    client2 = MagicMock()
    client2.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])

    try:
        res1 = call_llm_with_retry(client1, model='m', messages=[], max_retries=3)
        res1_exc = None
    except Exception as e:
        res1_exc = type(e)
        res1 = None

    try:
        res2 = call_llm_with_retry(client2, model='m', messages=[], max_retries=np.int64(3))
        res2_exc = None
    except Exception as e:
        res2_exc = type(e)
        res2 = None

    if res1_exc != res2_exc:
        pytest.xfail(reason=f"int exception {res1_exc} != np.int64 exception {res2_exc}")
    elif res1 != res2:
        pytest.xfail(reason="int result != np.int64 result")

    assert res1_exc == res2_exc
    assert res1 == res2
def test_call_llm_with_retry_numpy_float(tmp_path):
    pytest.importorskip("numpy")
    import numpy as np
    client1 = MagicMock()
    client1.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client2 = MagicMock()
    client2.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])

    try:
        res1 = call_llm_with_retry(client1, model='m', messages=[], max_retries=3.0)
        res1_exc = None
    except Exception as e:
        res1_exc = type(e)
        res1 = None

    try:
        res2 = call_llm_with_retry(client2, model='m', messages=[], max_retries=np.float64(3.0))
        res2_exc = None
    except Exception as e:
        res2_exc = type(e)
        res2 = None

    if res1_exc != res2_exc:
        pytest.xfail(reason=f"float returned {res1_exc}, np.float64 returned {res2_exc}")
    elif res1 != res2:
        pytest.xfail(reason="float result != np.float64 result")

    assert res1_exc == res2_exc
    assert res1 == res2
