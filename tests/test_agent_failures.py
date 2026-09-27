import sys
import pytest
from unittest.mock import MagicMock

def test_humboldt_provider_failure_does_not_crash(mocker, capsys):
    import humboldt

    mocker.patch.object(sys, 'argv', ['humboldt.py', '--skip-deps'])

    inputs = ["Where is the Eiffel Tower?", "exit"]
    mocker.patch('builtins.input', side_effect=inputs)

    mock_openai_class = mocker.patch('openai.OpenAI')
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Simulate a provider failure
    mock_client.chat.completions.create.side_effect = Exception("API connection timed out")

    try:
        humboldt.main()
    except Exception as e:
        pytest.fail(f"humboldt.main() crashed instead of handling the provider failure: {e}")

    captured = capsys.readouterr()
    assert "Exiting Humboldt" in captured.out

def test_geoai_cli_chat_provider_failure(mocker, capsys):
    import geoai_cli

    mocker.patch.object(sys, 'argv', ['geoai_cli.py', 'chat'])

    inputs = ["Where is the Eiffel Tower?", "exit"]
    mocker.patch('builtins.input', side_effect=inputs)

    mock_openai_class = mocker.patch('openai.OpenAI')
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_client.chat.completions.create.side_effect = Exception("API connection timed out")

    try:
        geoai_cli.main()
    except Exception as e:
        if not isinstance(e, SystemExit):
            pytest.fail(f"geoai_cli.main() crashed instead of handling the provider failure: {e}")

    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out
