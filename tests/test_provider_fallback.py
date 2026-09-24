import pytest
import sys
from unittest.mock import patch, MagicMock
import geocode

def test_geocode_provider_fallback(capsys):
    with patch('geocode.OpenAI') as mock_openai, \
         patch('sys.argv', ['geocode.py']), \
         patch('builtins.input', return_value='San Francisco'), \
         patch('time.sleep'):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Simulate 2 failures then a success
        mock_client.chat.completions.create.side_effect = [
            Exception("Connection error"),
            Exception("Timeout"),
            MagicMock(choices=[MagicMock(message=MagicMock(function_call=None, content="Fallback success"))])
        ]

        geocode.main()

        assert mock_client.chat.completions.create.call_count == 3

        captured = capsys.readouterr()
        assert "Fallback success" in captured.out or "San Francisco" in captured.out

def test_geocode_provider_fallback_exhaustion(capsys):
    with patch('geocode.OpenAI') as mock_openai, \
         patch('sys.argv', ['geocode.py']), \
         patch('builtins.input', return_value='San Francisco'), \
         patch('time.sleep'):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Simulate 3 failures
        mock_client.chat.completions.create.side_effect = [
            Exception("Connection error"),
            Exception("Timeout"),
            Exception("Service unavailable")
        ]

        with pytest.raises(ValueError, match="exhausted"):
            geocode.main()

        assert mock_client.chat.completions.create.call_count == 3
