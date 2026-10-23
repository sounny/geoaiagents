import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="hello")])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()

@patch('time.sleep')
def test_call_llm_with_retry_timeout_then_success(mock_sleep):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="hello")])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.parametrize("text_input", [
    "",
    "   ",
    "\t padded string \n"
])
def test_call_llm_with_retry_edge_case_texts_in_kwargs(text_input):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message="hello")])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(
        client,
        model=text_input,
        messages=[{"role": "user", "content": text_input}],
        max_retries=3
    )

    assert response == expected_response
    client.chat.completions.create.assert_called_once_with(
        model=text_input,
        messages=[{"role": "user", "content": text_input}]
    )

@patch('time.sleep')
@pytest.mark.parametrize("text_output", [
    "",
    "   ",
    "\t padded string \n"
])
def test_call_llm_with_retry_edge_case_texts_in_response(mock_sleep, text_output):
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=text_output)])
    client.chat.completions.create.return_value = expected_response

    if not text_output:
        with pytest.raises(ValueError, match="LLM call failed after 3 attempts: Malformed response: 'message' missing or empty in first choice"):
            call_llm_with_retry(client, model='m', messages=[], max_retries=3)
    else:
        response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)
        assert response == expected_response
