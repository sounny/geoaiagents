import pytest
from tool_registry import parse_tool_args, ToolRegistry, create_registry, ToolDefinition

def test_parse_tool_args_dict():
    assert parse_tool_args({"key": "value"}) == {"key": "value"}

def test_parse_tool_args_valid_json():
    assert parse_tool_args('{"key": "value"}') == {"key": "value"}

def test_parse_tool_args_invalid_json():
    assert parse_tool_args('{"key": "value"') == {}

def test_parse_tool_args_json_array():
    assert parse_tool_args('["value"]') == {}

def test_parse_tool_args_empty_string():
    assert parse_tool_args("") == {}
    assert parse_tool_args(None) == {}

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

def test_tool_definition_fields():
    def dummy_handler(args):
        return "dummy"

    td = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
        handler=dummy_handler
    )

    assert td.name == "test_tool"
    assert td.description == "A test tool"
    assert td.parameters == {"type": "object", "properties": {}}
    assert td.handler({"test": "value"}) == "dummy"

def test_create_registry_unique_tool_names():
    registry = create_registry()
    tools = registry.openai_functions()

    names = [tool["name"] for tool in tools]

    assert len(names) > 0
    assert all(isinstance(name, str) and len(name) > 0 for name in names)
    assert len(names) == len(set(names))
