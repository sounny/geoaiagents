import pytest
from unittest.mock import MagicMock, patch
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_success():
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = ["some_choice"]
    client.chat.completions.create.return_value = mock_response

    response = call_llm_with_retry(client, max_retries=3)
    assert response == mock_response
    assert client.chat.completions.create.call_count == 1

@patch("time.sleep")
def test_call_llm_with_retry_malformed(mock_sleep):
    client = MagicMock()
    mock_response = MagicMock()
    # Malformed because it lacks 'choices' or choices is empty
    mock_response.choices = []
    client.chat.completions.create.return_value = mock_response

    with pytest.raises(ValueError, match="LLM call failed after 3 attempts"):
        call_llm_with_retry(client, max_retries=3)

    assert client.chat.completions.create.call_count == 3
    assert mock_sleep.call_count == 2

@patch("time.sleep")
def test_call_llm_with_retry_timeout_then_success(mock_sleep):
    client = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = ["some_choice"]

    # Fail first two times, succeed on the third
    client.chat.completions.create.side_effect = [
        TimeoutError("Request timed out"),
        ValueError("Something went wrong"),
        mock_response
    ]

    response = call_llm_with_retry(client, max_retries=3)

    assert response == mock_response
    assert client.chat.completions.create.call_count == 3
    assert mock_sleep.call_count == 2

@patch("time.sleep")
@patch("llm_utils.logging.warning")
@patch("llm_utils.logging.exception")
def test_call_llm_with_retry_logging(mock_exception, mock_warning, mock_sleep):
    client = MagicMock()
    client.chat.completions.create.side_effect = ValueError("Some LLM Error")

    with pytest.raises(ValueError, match="LLM call failed after 3 attempts"):
        call_llm_with_retry(client, max_retries=3)

    assert mock_exception.call_count == 1
    assert mock_warning.call_count == 2
    # Verify exc_info=True was passed to warning
    mock_warning.assert_called_with(f"LLM call failed on attempt 2: Some LLM Error. Retrying...", exc_info=True)
