import pytest
from unittest.mock import MagicMock
import sys

from tool_registry import parse_tool_args, create_registry
import humboldt
import geoai_cli

def test_parse_tool_args_malformed():
    """Test that malformed JSON from a provider is handled gracefully."""
    assert parse_tool_args("{invalid json") == {}
    assert parse_tool_args("") == {}
    assert parse_tool_args(None) == {}
    assert parse_tool_args("[]") == {}

def test_tool_failure_propagation():
    """Test that tool exceptions are propagated as text for the provider to see."""
    registry = create_registry()

    def failing_handler(args):
        raise ValueError("Simulated API timeout")

    registry.register_tool(
        name="flaky_tool",
        description="A tool that always fails",
        parameters={},
        handler=failing_handler
    )

    result = registry.invoke("flaky_tool", "{}")
    assert result is not None
    assert "Error running flaky_tool: Simulated API timeout" in result

def test_retry_exhaustion_humboldt(mocker, capsys):
    """Test that Humboldt loop exhausts gracefully when max steps are reached."""
    mock_client = mocker.MagicMock()
    mock_msg = mocker.MagicMock()
    mock_msg.content = None
    mock_msg.function_call = mocker.MagicMock()
    mock_msg.function_call.name = "geocode_locations"
    mock_msg.function_call.arguments = '{"locations": "Paris"}'

    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock(message=mock_msg)]
    mock_client.chat.completions.create.return_value = mock_resp

    mocker.patch("openai.OpenAI", return_value=mock_client)
    mocker.patch("humboldt.check_and_install_dependencies")
    mocker.patch("builtins.input", side_effect=["find Paris", "exit"])
    mocker.patch("sys.argv", ["humboldt.py", "--max-steps", "2"])

    humboldt.main()

    captured = capsys.readouterr()
    assert "[INFO] Reached maximum tool-call steps" in captured.out
    assert mock_client.chat.completions.create.call_count == 3

def test_retry_exhaustion_geoai_cli(mocker, capsys):
    """Test that GeoAI CLI chat loop exhausts gracefully when max steps are reached."""
    mock_client = mocker.MagicMock()
    mock_msg = mocker.MagicMock()
    mock_msg.content = None
    mock_msg.function_call = mocker.MagicMock()
    mock_msg.function_call.name = "geocode_locations"
    mock_msg.function_call.arguments = '{"locations": "London"}'

    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock(message=mock_msg)]
    mock_client.chat.completions.create.return_value = mock_resp

    mocker.patch("openai.OpenAI", return_value=mock_client)
    mocker.patch("builtins.input", side_effect=["find London", "exit"])
    mocker.patch("sys.argv", ["geoai_cli.py", "chat", "--max-steps", "1"])

    try:
        geoai_cli.main()
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert "[INFO] Reached max tool-call steps for this turn." in captured.out
    assert mock_client.chat.completions.create.call_count == 2
