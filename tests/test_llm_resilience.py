import pytest
from unittest.mock import patch, MagicMock
import sys

# Test that when OpenAI client returns an empty choice list (or no choices attr),
# the orchestration loops gracefully handle it and don't crash.

def test_humboldt_handles_empty_choices(capsys):
    from humboldt import main

    with patch('openai.OpenAI') as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client

        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        # Mock inputs: user says something, then exit
        with patch('builtins.input', side_effect=['Hello', 'exit']):
            with patch.object(sys, 'argv', ['humboldt.py']):
                main()

    captured = capsys.readouterr()
    assert "[ERROR] Invalid or empty response from LLM provider." in captured.out
    assert "Exiting Humboldt. Goodbye!" in captured.out

def test_geocode_handles_empty_choices(capsys):
    from geocode import main

    with patch('geocode.OpenAI') as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client

        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        with patch('builtins.input', return_value='Paris'):
            with patch.object(sys, 'argv', ['geocode.py']):
                main()

    captured = capsys.readouterr()
    assert "[ERROR] Invalid or empty response from LLM provider." in captured.out

def test_geoai_cli_handles_empty_choices(capsys):
    from geoai_cli import main

    with patch('openai.OpenAI') as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client

        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        with patch('builtins.input', side_effect=['Hello', 'exit']):
            with patch.object(sys, 'argv', ['geoai_cli.py', 'chat']):
                # geoai_cli main returns a status code
                result = main()
                assert result == 0

    captured = capsys.readouterr()
    assert "[ERROR] Invalid or empty response from LLM provider." in captured.out

def test_webchat_handles_empty_choices():
    from webchat import chat

    with patch('webchat.client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        history, msgs, _, _ = chat("Hello", [], None)
        assert history[-1]['role'] == "assistant"
        assert "invalid or empty response" in history[-1]['content'].lower()
