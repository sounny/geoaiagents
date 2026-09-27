import pytest
import openai
from unittest.mock import patch, MagicMock

import geoai_cli

@patch("openai.resources.chat.completions.Completions.create")
def test_geoai_cli_unavailable_provider(mock_create, capsys, monkeypatch):
    # Mock create to raise APIConnectionError
    mock_create.side_effect = openai.APIConnectionError(request=MagicMock())

    # Mock input to send a message and then exit
    input_generator = (m for m in ["hello", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_generator))

    args = argparse_mock = MagicMock()
    args.base_url = "http://localhost:9999/v1/"
    args.api_key = "test"
    args.model = "test"
    args.max_steps = 3
    args.debug = False

    registry = MagicMock()
    registry.openai_functions.return_value = []

    # Run the chat mode
    geoai_cli._run_chat_mode(args, registry)

    captured = capsys.readouterr()
    # It should not crash, but rather print an error and continue (or exit gracefully)
    assert "error" in captured.out.lower() or "connection" in captured.out.lower()

@patch("openai.resources.chat.completions.Completions.create")
def test_humboldt_unavailable_provider(mock_create, capsys, monkeypatch):
    import humboldt

    # Mock create to raise APIConnectionError
    mock_create.side_effect = openai.APIConnectionError(request=MagicMock())

    # Mock input to send a message and then exit
    input_generator = (m for m in ["hello", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_generator))

    # Patch sys.argv for argument parsing
    monkeypatch.setattr("sys.argv", ["humboldt.py", "--base-url", "http://localhost:9999/v1/", "--model", "test", "--skip-deps"])

    # Run the main mode
    humboldt.main()

    captured = capsys.readouterr()
    assert "Error communicating with AI provider" in captured.out

@patch("openai.resources.chat.completions.Completions.create")
def test_webchat_unavailable_provider(mock_create):
    import webchat

    # Mock create to raise APIConnectionError
    mock_create.side_effect = openai.APIConnectionError(request=MagicMock())

    # Run the chat mode
    reply, map_html, logs, table = webchat.respond("hello", [])

    assert "Error communicating with AI provider" in reply

@patch("openai.resources.chat.completions.Completions.create")
def test_geocode_unavailable_provider(mock_create, capsys, monkeypatch):
    import geocode

    # Mock create to raise APIConnectionError
    mock_create.side_effect = openai.APIConnectionError(request=MagicMock())

    # Mock input to send a message
    monkeypatch.setattr("builtins.input", lambda _: "Paris, France")

    # Patch sys.argv for argument parsing
    monkeypatch.setattr("sys.argv", ["geocode.py", "--base-url", "http://localhost:9999/v1/"])

    # Run the main mode
    geocode.main()

    captured = capsys.readouterr()
    assert "Error communicating with AI provider" in captured.out
    assert "Falling back to direct tool execution" in captured.out

def test_tool_registry_malformed_json():
    import tool_registry

    registry = tool_registry.create_registry()

    # Passing malformed JSON to parse_tool_args
    # Assuming tool_registry handles parsing and catches JSON errors
    args = tool_registry.parse_tool_args("not json")
    assert args == {}

    args2 = tool_registry.parse_tool_args("{'malformed': True}")
    assert args2 == {}
