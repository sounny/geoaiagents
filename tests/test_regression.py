import pytest
from unittest.mock import patch, MagicMock

import humboldt
import geoai_cli
import webchat
import geocode

def test_humboldt_api_orchestration_error():
    """Test humboldt handles LLM empty choices/malformed response gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[])

    with patch("openai.OpenAI", return_value=mock_client):
        # We need to mock input and registry
        with patch("builtins.input", side_effect=["test query", "exit", "exit"]):
            with patch("sys.argv", ["humboldt.py"]):  # mock args
                with patch("sys.stdout") as mock_stdout:
                    try:
                        humboldt.main()
                    except SystemExit:
                        pass
                    # The LLM try/except in humboldt triggers a 'break' and prints an error
                    error_logged = any("Provider orchestration failed" in str(call) for call in mock_stdout.mock_calls)
                    # It should also loop cleanly without raising an exception to the user
                    assert error_logged  # Make sure the error was logged gracefully

def test_geocode_global_rate_limiter():
    """Test geocode.py has global rate limiters initialized with max_retries."""
    assert hasattr(geocode, "_geocode_throttle")
    assert hasattr(geocode, "_reverse_throttle")

    assert geocode._geocode_throttle.max_retries == 2
    assert geocode._reverse_throttle.max_retries == 2

def test_webchat_api_orchestration_error():
    """Test webchat handles LLM empty choices/malformed response gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[])

    with patch("webchat.client", mock_client):
        history = []
        gen = webchat.respond("test message", history, None)
        res = list(gen)
        # Should have appended the error to history
        assert "Provider orchestration failed" in history[-1]["content"]
