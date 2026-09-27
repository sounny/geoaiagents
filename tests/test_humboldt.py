import pytest
from unittest.mock import patch, MagicMock
import humboldt
import sys

@patch("openai.OpenAI")
@patch("sys.argv", ["humboldt.py", "--skip-deps"])
@patch("humboldt.check_and_install_dependencies")
def test_main_llm_exception_handling(mock_check_deps, mock_openai, capsys):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Timeout")

    with patch("builtins.input", side_effect=["Test Location", "exit"]):
        with patch("logging.exception") as mock_logging:
            humboldt.main()

    captured = capsys.readouterr()
    assert "Encountered an error communicating with the AI. Please try again." in captured.out
    mock_logging.assert_called_once()
    assert "LLM API error during completion: %s" in mock_logging.call_args[0][0]
