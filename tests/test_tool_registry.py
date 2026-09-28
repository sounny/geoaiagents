import pytest
from tool_registry import parse_tool_args, ToolRegistry, create_registry

def test_parse_tool_args_dict():
    # Direct dictionary passthrough
    assert parse_tool_args({"key": "value"}) == {"key": "value"}

def test_parse_tool_args_valid_json():
    # Valid JSON string parses to dictionary
    assert parse_tool_args('{"key": "value"}') == {"key": "value"}

def test_parse_tool_args_invalid_json():
    # Invalid JSON string throws JSONDecodeError and falls back to empty dict
    assert parse_tool_args('{"key": "value"') == {}

def test_parse_tool_args_json_array():
    # JSON array parses but falls back to empty dict since it's not a dict
    assert parse_tool_args('["value"]') == {}

def test_parse_tool_args_empty_string():
    # Empty string or None falls back to empty dict
    assert parse_tool_args("") == {}
    assert parse_tool_args(None) == {}

def test_parse_tool_args_list():
    # A raw list input falls through the type checks and returns empty dict
    assert parse_tool_args(["value"]) == {}

def test_tool_registry_invoke_error_reporting():
    registry = ToolRegistry()

    def buggy_handler(args):
        raise ValueError("Simulated error")

    registry.register_tool(
        name="buggy_tool",
        description="A buggy tool",
        parameters={},
        handler=buggy_handler
    )

    result = registry.invoke("buggy_tool", {})
    assert "Error running buggy_tool: Simulated error" in result

def test_tool_registry_invoke_missing_tool():
    registry = ToolRegistry()
    result = registry.invoke("missing_tool", {})
    assert result is None
