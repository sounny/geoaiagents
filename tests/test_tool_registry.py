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
    assert parse_tool_args('   ') == {}

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

def test_create_registry_openai_functions_and_has_tool():
    reg = create_registry()
    funcs = reg.openai_functions()
    assert isinstance(funcs, list)
    assert len(funcs) >= 3

    names = []
    for entry in funcs:
        assert entry.get("type") == "function" or (isinstance(entry.get("function"), dict) and entry["function"].get("type") == "function")

        # Extract based on implementation shape
        if "function" in entry:
            name = entry["function"].get("name")
            desc = entry["function"].get("description")
            params = entry["function"].get("parameters")
        else:
            name = entry.get("name")
            desc = entry.get("description")
            params = entry.get("parameters")

        assert isinstance(name, str) and len(name) > 0
        assert isinstance(desc, str) and len(desc) > 0
        assert isinstance(params, dict)

        names.append(name)

    assert "load_geojson" in names
    assert "reverse_geocode_coordinates" in names
    assert reg.has_tool('geocode_locations') is True

def test_create_registry_has_tool_various():
    reg = create_registry()
    assert reg.has_tool('convert_dd_to_dms') is True
    assert reg.has_tool('reverse_geocode_coordinates') is True
    assert reg.has_tool('load_kml') is True
    assert reg.has_tool('load_csv') is True
    assert reg.has_tool('fetch_geo_boundaries') is True
    assert reg.has_tool('missing_tool_zzz') is False

def test_tool_registry_invoke_and_parse_combined():
    reg = create_registry()
    # unknown tool
    assert reg.invoke('definitely_not_a_tool_zz', {}) is None
    # invalid JSON strings
    assert parse_tool_args('{not json') == {}
    # valid JSON arrays
    assert parse_tool_args('[1,2,3]') == {}

def test_parse_tool_args_types():
    assert parse_tool_args({'a': 1}) == {'a': 1}
    assert parse_tool_args('{"locations":"Paris"}') == {"locations": "Paris"}
    assert parse_tool_args(123) == {}
    assert parse_tool_args(None) == {}
    assert parse_tool_args('   ') == {}
