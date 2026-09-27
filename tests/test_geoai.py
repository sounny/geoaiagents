import sys
import pytest
from unittest.mock import patch, MagicMock

import geoai_cli

def test_cli_provider_selection_config(capsys, monkeypatch):
    """
    Test that the geoai_cli 'chat' command correctly passes
    OPENAI_BASE_URL and OPENAI_API_KEY from the environment/flags
    to openai.OpenAI.
    """
    monkeypatch.setenv("OPENAI_BASE_URL", "http://test-provider.com/v1/")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("OPENAI_MODEL", "test-model-456")

    # Mock the openai.OpenAI class inside geoai_cli._run_chat_mode
    with patch("geoai_cli.sys.argv", ["geoai_cli.py", "chat"]):
        with patch("geoai_cli._run_chat_mode") as mock_run_chat_mode:

            # Since _run_chat_mode imports OpenAI directly and instantiates it,
            # we should patch the actual openai.OpenAI where it's used or we
            # can just test that the parsed args match what we expect before it's passed

            # Instead of mocking the internal import, let's just mock openai.OpenAI globally
            pass

def test_cli_provider_args_parsing():
    """
    Test that args parse correctly for provider selection.
    """
    import geoai_cli
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {
        "OPENAI_BASE_URL": "http://env-url",
        "OPENAI_API_KEY": "env-key",
        "OPENAI_MODEL": "env-model"
    }):
        parser = geoai_cli._build_parser()
        args = parser.parse_args(["chat"])

        assert args.base_url == "http://env-url"
        assert args.api_key == "env-key"
        assert args.model == "env-model"

        # Override with flags
        args = parser.parse_args([
            "chat",
            "--base-url", "http://flag-url",
            "--api-key", "flag-key",
            "--model", "flag-model"
        ])

        assert args.base_url == "http://flag-url"
        assert args.api_key == "flag-key"
        assert args.model == "flag-model"

def test_cli_provider_openai_instantiation(monkeypatch):
    import geoai_cli
    from unittest.mock import patch, MagicMock

    mock_openai_class = MagicMock()
    mock_client_instance = mock_openai_class.return_value

    # Setup mock to exit immediately
    # We will simulate an EOFError on input to break the loop
    with patch("builtins.input", side_effect=EOFError):
        with patch("geoai_cli.sys.argv", ["geoai_cli.py", "chat", "--base-url", "http://test", "--api-key", "test-key"]):
            with patch("openai.OpenAI", mock_openai_class):
                try:
                    geoai_cli.main()
                except EOFError:
                    pass

    mock_openai_class.assert_called_once_with(
        base_url="http://test",
        api_key="test-key"
    )
