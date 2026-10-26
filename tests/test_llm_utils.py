import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: True is treated as 1 instead of raising TypeError")
def test_call_llm_with_retry_true_retries(tmp_path):
    client = MagicMock()
    expected = SimpleNamespace(choices=[SimpleNamespace(message="test")])
    client.chat.completions.create.return_value = expected

    try:
        call_llm_with_retry(client, max_retries=True)
    except TypeError:
        pass
    else:
        raise AssertionError("Should have raised TypeError for bool max_retries")

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: False is treated as 0 and raises ValueError instead of TypeError")
def test_call_llm_with_retry_false_retries(tmp_path):
    client = MagicMock()
    expected = SimpleNamespace(choices=[SimpleNamespace(message="test")])
    client.chat.completions.create.return_value = expected

    try:
        call_llm_with_retry(client, max_retries=False)
    except TypeError:
        pass
    except ValueError as e:
        raise AssertionError(f"Raised ValueError instead of TypeError: {e}") from e
    else:
        raise AssertionError("Should have raised TypeError for bool max_retries")

def test_call_llm_with_retry_negative_zero_retries(tmp_path):
    client = MagicMock()
    expected = SimpleNamespace(choices=[SimpleNamespace(message="test")])
    client.chat.completions.create.return_value = expected

    with pytest.raises(TypeError, match="'float' object cannot be interpreted as an integer"):
        call_llm_with_retry(client, max_retries=-0.0)
