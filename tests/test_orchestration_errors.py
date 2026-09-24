import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Ensure the root directory is accessible for imports (similar to pytest.ini)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import humboldt
import geoai_cli
import geocode
import webchat

def test_humboldt_retry_empty_choices(monkeypatch):
    """Test humboldt.py retries when response.choices is empty."""
    monkeypatch.setattr("sys.argv", ["humboldt.py", "--max-steps", "1"])

    # Mock OpenAI client
    mock_client = MagicMock()
    # First response: empty choices, Second response: valid choices
    mock_response_empty = MagicMock()
    mock_response_empty.choices = []

    mock_response_valid = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test success"
    mock_message.function_call = None
    mock_response_valid.choices = [MagicMock(message=mock_message)]

    mock_client.chat.completions.create.side_effect = [mock_response_empty, mock_response_valid]

    with patch("openai.OpenAI", return_value=mock_client), \
         patch("builtins.input", side_effect=["test message", "exit"]), \
         patch("sys.stdout"), \
         patch("time.sleep"):
        humboldt.main()

    assert mock_client.chat.completions.create.call_count >= 2

def test_geoai_cli_retry_exception(monkeypatch):
    """Test geoai_cli.py retries when an exception occurs."""
    monkeypatch.setattr("sys.argv", ["geoai_cli.py", "chat", "--max-steps", "1"])

    # Mock OpenAI client
    mock_client = MagicMock()

    mock_response_valid = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test success CLI"
    mock_message.function_call = None
    mock_response_valid.choices = [MagicMock(message=mock_message)]

    # First fails with Exception, Second succeeds
    mock_client.chat.completions.create.side_effect = [Exception("API Timeout"), mock_response_valid]

    with patch("openai.OpenAI", return_value=mock_client), \
         patch("builtins.input", side_effect=["test query", "exit"]), \
         patch("sys.stdout"), \
         patch("time.sleep"):
        # Run CLI loop
        try:
            geoai_cli.main()
        except SystemExit:
            pass

    assert mock_client.chat.completions.create.call_count >= 2

def test_geocode_retry_empty_choices(monkeypatch):
    """Test geocode.py retries on empty choices."""
    monkeypatch.setattr("sys.argv", ["geocode.py"])

    # Mock OpenAI client
    mock_client = MagicMock()

    mock_response_empty = MagicMock()
    mock_response_empty.choices = []

    mock_response_valid = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "Geocoded results"
    mock_response_valid.choices = [MagicMock(message=mock_message)]

    mock_client.chat.completions.create.side_effect = [mock_response_empty, mock_response_valid]

    with patch("geocode.OpenAI", return_value=mock_client, create=True), \
         patch("builtins.input", return_value="Paris, France"), \
         patch("geocode.geocode_locations", return_value="mock table"), \
         patch("sys.stdout"), \
         patch("time.sleep"):
        geocode.main()

    assert mock_client.chat.completions.create.call_count >= 2

def test_webchat_retry_exception():
    """Test webchat.py respond function retries on Exception."""
    # Mock OpenAI client globally inside webchat
    mock_client = MagicMock()

    mock_response_valid = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Webchat response"
    mock_message.function_call = None
    mock_response_valid.choices = [MagicMock(message=mock_message)]

    # Fail once, succeed once
    mock_client.chat.completions.create.side_effect = [Exception("API error"), mock_response_valid]

    with patch("webchat.client", mock_client):
        # We also need to mock time.sleep to speed up tests
        with patch("time.sleep", return_value=None):
            reply, map_html, log_history, table = webchat.respond("Hello webchat", [])

    assert reply == "Webchat response"
    assert mock_client.chat.completions.create.call_count == 2

def test_humboldt_retry_exhaustion(monkeypatch):
    """Test humboldt.py throws exception if choices are empty 3 times."""
    monkeypatch.setattr("sys.argv", ["humboldt.py", "--max-steps", "1"])

    mock_client = MagicMock()
    mock_response_empty = MagicMock()
    mock_response_empty.choices = []

    mock_client.chat.completions.create.side_effect = [mock_response_empty] * 3

    with patch("openai.OpenAI", return_value=mock_client), \
         patch("builtins.input", side_effect=["test message", "exit"]), \
         patch("sys.stdout"), \
         patch("time.sleep"), \
         pytest.raises(ValueError, match="Empty choices returned after 3 attempts"):
        humboldt.main()

    assert mock_client.chat.completions.create.call_count == 3
