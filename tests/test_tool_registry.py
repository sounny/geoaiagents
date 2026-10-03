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

def test_default_tool_coord_parsers_keys_and_values():
    from tool_registry import DEFAULT_TOOL_COORD_PARSERS

    expected_keys = {
        'geocode_locations',
        'convert_dd_to_dms',
        'reverse_geocode_coordinates',
        'load_geojson',
        'load_kml',
        'load_csv',
        'fetch_geo_boundaries',
        'calculate_distance'
    }

    for key in expected_keys:
        assert key in DEFAULT_TOOL_COORD_PARSERS

    assert DEFAULT_TOOL_COORD_PARSERS['calculate_distance'] == 'distance'
    assert DEFAULT_TOOL_COORD_PARSERS['geocode_locations'] == (2, 3)
