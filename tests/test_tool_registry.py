import pytest
from tool_registry import create_registry, ToolRegistry, parse_tool_args

def test_parse_tool_args():
    # Valid JSON string
    assert parse_tool_args('{"key": "value"}') == {"key": "value"}

    # Empty string
    assert parse_tool_args("") == {}

    # Invalid JSON string
    assert parse_tool_args('{"key": "value"') == {}

    # Dictionary
    assert parse_tool_args({"key": "value"}) == {"key": "value"}

def test_create_registry():
    registry = create_registry()

    assert registry.has_tool("geocode_locations")
    assert registry.has_tool("convert_dd_to_dms")
    assert registry.has_tool("reverse_geocode_coordinates")
    assert registry.has_tool("calculate_distance")
    assert registry.has_tool("load_geojson")
    assert registry.has_tool("load_kml")
    assert registry.has_tool("load_csv")
    assert registry.has_tool("fetch_geo_boundaries")

    functions = registry.openai_functions()
    assert len(functions) >= 8

def test_invoke_tool():
    registry = ToolRegistry()
    registry.register_tool(
        name="test_tool",
        description="A test tool",
        parameters={},
        handler=lambda args: f"Success: {args.get('input')}"
    )

    # Successful invocation
    assert registry.invoke("test_tool", '{"input": "data"}') == "Success: data"

    # Unknown tool
    assert registry.invoke("unknown_tool", '{"input": "data"}') is None

    # Error in tool
    registry.register_tool(
        name="error_tool",
        description="An error tool",
        parameters={},
        handler=lambda args: 1 / 0
    )
    result = registry.invoke("error_tool", "{}")
    assert result.startswith("Error running error_tool")
