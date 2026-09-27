import pytest
from unittest.mock import patch, MagicMock
import sys
import time

def test_humboldt_llm_error(capsys):
    with patch("openai.OpenAI") as mock_openai, \
         patch("sys.argv", ["humboldt.py", "--max-steps", "1", "--skip-deps"]), \
         patch("builtins.input", side_effect=["hello", "exit"]):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")

        from humboldt import main

        main()

        captured = capsys.readouterr()
        assert "API Timeout" in captured.out or "API Timeout" in captured.err or "Error communicating with LLM" in captured.out


def test_geoai_cli_llm_error(capsys):
    with patch("openai.OpenAI") as mock_openai, \
         patch("sys.argv", ["geoai_cli.py", "chat", "--max-steps", "1"]), \
         patch("builtins.input", side_effect=["hello", "exit"]):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")

        from geoai_cli import main

        main()

        captured = capsys.readouterr()
        assert "API Timeout" in captured.out or "API Timeout" in captured.err or "Error communicating with LLM" in captured.out

def test_geocode_llm_error(capsys):
    with patch("openai.OpenAI") as mock_openai, \
         patch("sys.argv", ["geocode.py"]), patch("builtins.input", side_effect=["test location", "exit"]):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")

        from geocode import main

        main()

        captured = capsys.readouterr()
        assert "API Timeout" in captured.out or "API Timeout" in captured.err or "Error communicating with LLM" in captured.out

def test_webchat_llm_error(capsys):
    with patch("webchat.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")

        from webchat import respond, client

        # Override the globally initialized client for the test
        import webchat
        webchat.client = mock_client

        reply, map_html, logs, table = respond("hello", [], None)

        assert "API Timeout" in reply or "Error communicating with LLM" in reply

def test_dd2dms_llm_error(capsys):
    with patch("openai.OpenAI") as mock_openai, \
         patch("sys.argv", ["dd2dms.py"]), patch("builtins.input", side_effect=["40.0, -100.0", "exit"]):

        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")

        from dd2dms import main

        try:
            main()
        except SystemExit:
            pass # We expect sys.exit(1) on error

        captured = capsys.readouterr()
        assert "API Timeout" in captured.out or "API Timeout" in captured.err or "Error communicating with LLM" in captured.out
