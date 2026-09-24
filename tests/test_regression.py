import pytest
from unittest.mock import patch, MagicMock

import humboldt
import geoai_cli
import webchat
import geocode

def test_humboldt_api_orchestration_error(capsys):
    """Test humboldt handles LLM empty choices/malformed response gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[])

    with patch("openai.OpenAI", return_value=mock_client):
        # We need to mock input and registry
        with patch("builtins.input", side_effect=["test query", "exit", "exit"]):
            with patch("sys.argv", ["humboldt.py"]):  # mock args
                try:
                    humboldt.main()
                except SystemExit:
                    pass
                # The LLM try/except in humboldt triggers a 'break' and prints an error
                captured = capsys.readouterr()
                error_logged = "Provider orchestration failed" in captured.out or "Provider orchestration failed" in captured.err
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

def test_geoai_cli_api_orchestration_error(capsys):
    """Test geoai_cli handles LLM empty choices/malformed response gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[])

    with patch("openai.OpenAI", return_value=mock_client):
        with patch("builtins.input", side_effect=["test query", "exit", "exit"]):
            with patch("sys.argv", ["geoai_cli.py", "chat"]):  # mock args
                try:
                    geoai_cli.main()
                except SystemExit:
                    pass
                captured = capsys.readouterr()
                error_logged = "Provider orchestration failed" in captured.out or "Provider orchestration failed" in captured.err
                assert error_logged
