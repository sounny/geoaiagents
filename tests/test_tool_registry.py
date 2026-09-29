import pytest
from tool_registry import parse_tool_args, ToolRegistry, create_registry

def test_parse_tool_args_dict():
    assert parse_tool_args({"key": "value"}) == {"key": "value"}

def test_parse_tool_args_valid_json():
    assert parse_tool_args('{"key": "value"}') == {"key": "value"}

def test_parse_tool_args_invalid_json():
    import pytest
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_tool_args('{"key": "value"')

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

def test_parse_tool_args_behavior():
    # list
    assert parse_tool_args(["a", "b"]) == {}
    # None
    assert parse_tool_args(None) == {}
    # empty string
    assert parse_tool_args("") == {}
    # invalid JSON raises ValueError
    try:
        parse_tool_args('{"a": 1')
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_invoke_raw_string_happy_path():
    registry = create_registry()
    res = registry.invoke("convert_dd_to_dms", "48.8566,2.3522")
    assert "Latitude (DMS)" in res or "Latitude" in res

def test_invoke_invalid_json():
    registry = create_registry()
    res = registry.invoke("convert_dd_to_dms", '{"coordinates": "48.8566,2.3522"')
    assert "Error running convert_dd_to_dms" in res
    assert "Invalid JSON" in res
