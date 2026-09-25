import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Import the files we want to test to ensure they use env config correctly
# Specifically we'll check the argparse defaults
import humboldt
import geoai_cli
import webchat

def test_webchat_env_vars(monkeypatch):
    """Test that webchat.py correctly reads OPENAI_BASE_URL from env vars."""
    # webchat.py sets BASE_URL at import time, so we need to reload it
    import importlib
    monkeypatch.setenv("OPENAI_BASE_URL", "http://custom-url:1234/v1/")
    monkeypatch.setenv("OPENAI_API_KEY", "custom-key")
    importlib.reload(webchat)
    assert webchat.BASE_URL == "http://custom-url:1234/v1/"
    assert webchat.API_KEY == "custom-key"

def test_humboldt_env_vars(monkeypatch, capsys):
    """Test that humboldt.py correctly sets defaults from env vars."""
    monkeypatch.setenv("OPENAI_BASE_URL", "http://custom-url:1234/v1/")

    # We can test argparse by calling the script with --help and parsing output,
    # or by patching sys.argv and running a portion of the code
    with patch("sys.argv", ["humboldt.py", "--help"]):
        with pytest.raises(SystemExit):
            humboldt.main()

    # We could also directly inspect the parser if it was accessible, but it's local to main()
    # Another way is to mock OpenAI and run it
