import pytest
from tool_registry import parse_tool_args, ToolRegistry, create_registry

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

def test_create_registry_openai_functions_schema_and_contents():
    registry = create_registry()
    funcs = registry.openai_functions()

    assert isinstance(funcs, list)
    assert len(funcs) > 0

    names = set()
    for func in funcs:
        assert isinstance(func, dict)
        assert "name" in func and isinstance(func["name"], str)
        assert "description" in func and isinstance(func["description"], str)
        assert "parameters" in func and isinstance(func["parameters"], dict)
        names.add(func["name"])

    assert 'load_geojson' in names
    assert 'reverse_geocode_coordinates' in names
