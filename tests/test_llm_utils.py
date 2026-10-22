import sys
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


@pytest.mark.parametrize("max_retries", [
    0,
    1,
    -sys.maxsize - 1,
    sys.maxsize,
])
def test_call_llm_with_retry_boundaries(max_retries):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])
    client.chat.completions.create.return_value = expected_response

    if max_retries <= 0:
        with pytest.raises(ValueError, match=f"LLM call failed after {max_retries} attempts"):
            call_llm_with_retry(client, model='m', messages=[], max_retries=max_retries)
        client.chat.completions.create.assert_not_called()
    else:
        response = call_llm_with_retry(client, model='m', messages=[], max_retries=max_retries)
        assert response == expected_response
        client.chat.completions.create.assert_called_once()

@pytest.mark.parametrize("max_retries", [
    "",
    "測試",
])
def test_call_llm_with_retry_type_errors(max_retries):
    client = MagicMock()
    with pytest.raises(TypeError, match="'str' object cannot be interpreted as an integer"):
        call_llm_with_retry(client, model='m', messages=[], max_retries=max_retries)
    client.chat.completions.create.assert_not_called()
