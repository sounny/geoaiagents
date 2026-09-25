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
                with patch("time.sleep"):
                    try:
                        humboldt.main()
                    except SystemExit:
                        pass
                    captured = capsys.readouterr()
                    assert "Provider orchestration failed" in captured.out

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
    """Test geoai_cli chat mode handles LLM empty choices/malformed response gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[])

    with patch("geoai_cli.OpenAI", return_value=mock_client, create=True):
        # We need to mock input and registry
        with patch("builtins.input", side_effect=["test query", "exit"]):
            with patch("sys.argv", ["geoai_cli.py", "chat"]):  # mock args
                with patch("time.sleep"):
                    try:
                        geoai_cli.main()
                    except SystemExit:
                        pass
                    captured = capsys.readouterr()
                    assert "Provider orchestration failed" in captured.out
