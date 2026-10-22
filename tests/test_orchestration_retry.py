import pytest
from unittest.mock import MagicMock, patch
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_success():
    client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message = "some_message"
    mock_response.choices = [mock_choice]
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
    mock_choice = MagicMock()
    mock_choice.message = "some_message"
    mock_response.choices = [mock_choice]

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

def test_call_llm_with_retry_happy_path_fast():
    """
    Test that a successful call does not invoke sleep or any retries.
    """
    from types import SimpleNamespace
    client = MagicMock()
    mock_response = SimpleNamespace(choices=[SimpleNamespace(message="happy_choice")])
    client.chat.completions.create.return_value = mock_response

    with patch('time.sleep') as mock_sleep:
        response = call_llm_with_retry(client, max_retries=3)

    assert response == mock_response
    assert client.chat.completions.create.call_count == 1
    mock_sleep.assert_not_called()

import os
from openai import OpenAI
import httpx

@pytest.mark.xfail(reason="Raises ValueError with raw traceback (__cause__) instead of a clean handled error message")
def test_call_llm_missing_api_key(monkeypatch, mocker):
    """
    Test that calling the LLM with every API key removed produces a clear error
    message rather than a raw traceback, with network mocked.
    """
    # Remove every API key environment variable dynamically
    for key in list(os.environ.keys()):
        if "API_KEY" in key or "ADMIN_KEY" in key:
            monkeypatch.delenv(key, raising=False)

    # Remove specifically known keys just in case
    for explicit_key in ["OPENAI_API_KEY", "OPENAI_ADMIN_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        monkeypatch.delenv(explicit_key, raising=False)

    # We must mock the network layer to ensure no real network requests are made.
    # The application defaults to "unused" when an API key is missing (e.g. in geoai_cli.py)
    # Since we are testing llm_utils.py, which accepts an already-instantiated client,
    # we instantiate it the same way the application does when keys are missing.
    client = OpenAI(api_key="unused", max_retries=0)

    # Mock the network transport layer to simulate an AuthenticationError (401)
    # which is what OpenAI's servers return when the key is "unused".
    mock_response = httpx.Response(
        status_code=401,
        json={
            "error": {
                "message": "Incorrect API key provided: unused.",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_api_key"
            }
        },
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    )
    mocker.patch("httpx.Client.send", return_value=mock_response)
    mocker.patch("time.sleep")

    with pytest.raises(Exception) as exc_info:
        call_llm_with_retry(
            client,
            max_retries=1,
            model="test-model",
            messages=[{"role": "user", "content": "hi"}]
        )

    # Asserting a clear error message rather than a raw traceback.
    # The application currently raises ValueError("...: {e}") from e.
    # The `from e` attaches the raw traceback via `__cause__`.
    assert exc_info.value.__cause__ is None, "A raw traceback was preserved via __cause__"
