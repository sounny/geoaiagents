import sys
import pytest
from unittest.mock import patch
import geoai_cli

@patch("openai.OpenAI")
def test_chat_mode_api_connection_failure(mock_openai, capsys):
    """Verify geoai_cli chat mode catches API connection errors gracefully."""
    # Setup mock client that raises an exception on chat.completions.create
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("Mock connection error")

    # Simulate running `geoai_cli chat` and sending one message
    test_args = ["geoai_cli.py", "chat"]
    inputs = ["hello", "exit"]

    with patch.object(sys, "argv", test_args):
        # We also need to patch input() to simulate user typing
        with patch("builtins.input", side_effect=inputs):
            geoai_cli.main()

    captured = capsys.readouterr()

    # Assert that the error was caught and printed, and we didn't crash
    assert "[ERROR] API connection failed: Mock connection error" in captured.out
    assert "Goodbye!" in captured.out
