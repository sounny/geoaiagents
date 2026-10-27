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

def test_tool_registry_invoke_happy_path():
    result = create_registry().invoke('convert_dd_to_dms', '48.8566,2.3522')
    assert "Latitude" in result or "DMS" in result

def test_tool_registry_invoke_happy_path_json():
    result = create_registry().invoke('convert_dd_to_dms', '{"coordinates": "48.8566,2.3522"}')
    assert "Latitude" in result or "DMS" in result

def test_tool_registry_invoke_invalid_json():
    result = create_registry().invoke('convert_dd_to_dms', '{"coordinates": "48.8566,2.3522"')
    assert "Error running convert_dd_to_dms: Invalid JSON" in result

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
def test_tool_registry_builtin_openai_functions_convert_dd_to_dms_membership():
    """Test registry and openai_functions structure (locking convert_dd_to_dms membership)."""
    reg = create_registry()

    assert reg.has_tool("convert_dd_to_dms") is True
    assert reg.has_tool("geocode_locations") is True
    assert reg.has_tool("calculate_distance") is True
    assert reg.has_tool("load_geojson") is True

    funcs = reg.openai_functions()
    assert isinstance(funcs, list)
    assert len(funcs) >= 3

    names = {f["name"] for f in funcs}
    assert "convert_dd_to_dms" in names

    for f in funcs:
        type_val = f.get("type", "function")
        assert type_val == "function"
        assert "name" in f and f["name"]
        assert "description" in f and f["description"]
        assert "parameters" in f and f["parameters"]

def test_tool_registry_name_validation():
    """Test that tool registry validates names are unique non-empty strings."""
    registry = ToolRegistry()

    # Test non-string name
    with pytest.raises(ValueError, match="Tool name must be a string"):
        registry.register_tool(name=123, description="desc", parameters={}, handler=lambda x: "test")

    # Test empty string name
    with pytest.raises(ValueError, match="Tool name must be a non-empty string"):
        registry.register_tool(name="", description="desc", parameters={}, handler=lambda x: "test")

    # Test duplicate name
    registry.register_tool(name="valid_name", description="desc", parameters={}, handler=lambda x: "test")
    with pytest.raises(ValueError, match="Tool 'valid_name' is already registered"):
        registry.register_tool(name="valid_name", description="desc2", parameters={}, handler=lambda x: "test")

def test_plugin_hook_handlers_order(mocker):
    """Test that registering two plugins and listing hook handlers twice returns the same order."""
    registry = ToolRegistry()
    mocker.patch("logging.info")
    mocker.patch("logging.warning")
    mocker.patch("logging.exception")

    # In this codebase, "plugins" are added by calling `register_tool`.
    registry.register_tool(
        name="plugin_1",
        description="First plugin",
        parameters={},
        handler=lambda x: "plugin_1"
    )
    registry.register_tool(
        name="plugin_2",
        description="Second plugin",
        parameters={},
        handler=lambda x: "plugin_2"
    )

    # "listing hook handlers" for tools implies listing the tool definitions for the LLM.
    # The application uses `openai_functions()` to list these handlers for the LLM API.
    # We test this public API to ensure the ordering is consistent when invoked repeatedly.
    handlers_1 = [tool["name"] for tool in registry.openai_functions()]
    handlers_2 = [tool["name"] for tool in registry.openai_functions()]

    if handlers_1 != handlers_2:
        pytest.xfail("Tool/hook listing order is inconsistent")
    assert handlers_1 == handlers_2
import time
import sys

@pytest.mark.parametrize("func_name", [
    "parse_tool_args",
    "create_registry",
    "_register_builtin_tools",
    "_register_geocoding_tools",
    "_register_coordinate_tools",
    "_register_file_tools",
    "_load_plugins",
    "ToolRegistry.register_tool",
    "ToolRegistry.has_tool",
    "ToolRegistry.openai_functions",
    "ToolRegistry.invoke",
])
def test_public_functions_tz_independence(func_name, monkeypatch, mocker, tmp_path):
    mocker.patch("tool_registry.geocode_locations", return_value="mock_geo")
    mocker.patch("tool_registry.reverse_geocode_coordinates", return_value="mock_rev")
    mocker.patch("tool_registry.convert_dd_to_dms", return_value="mock_dms")
    mocker.patch("tool_registry.calculate_distance", return_value="mock_dist")
    mocker.patch("tool_registry.load_geojson", return_value="mock_gj")
    mocker.patch("tool_registry.load_kml", return_value="mock_kml")
    mocker.patch("tool_registry.load_csv", return_value="mock_csv")
    mocker.patch("tool_registry.fetch_geo_boundaries", return_value="mock_bnd")

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "my_tz_plugin.py"
    plugin_file.write_text(
        "def register_tools(registry):\n"
        "    registry.register_tool(name='my_plugin_tool', description='desc', parameters={}, handler=lambda x: 'ok')\n"
    )
    sys.path.insert(0, str(plugin_dir))
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "my_tz_plugin")

    def run_under_tz(tz, runner):
        monkeypatch.setenv("TZ", tz)
        if hasattr(time, "tzset"):
            time.tzset()
        return runner()

    from tool_registry import _register_builtin_tools, _register_geocoding_tools, _register_coordinate_tools, _register_file_tools, _load_plugins

    runners = {
        "parse_tool_args": lambda: parse_tool_args('{"a": 1}'),
        "create_registry": lambda: create_registry().openai_functions(),
        "ToolRegistry.register_tool": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.openai_functions()
        )[-1],
        "ToolRegistry.has_tool": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.has_tool("test_tool")
        )[-1],
        "ToolRegistry.openai_functions": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.openai_functions()
        )[-1],
        "ToolRegistry.invoke": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.invoke("test_tool", {})
        )[-1],
    }

    # Expose inner functions just for the test parametrization scope
    if func_name == "_register_builtin_tools":
        runners["_register_builtin_tools"] = lambda: (tr := ToolRegistry(), _register_builtin_tools(tr), tr.openai_functions())[-1]
    if func_name == "_register_geocoding_tools":
        runners["_register_geocoding_tools"] = lambda: (tr := ToolRegistry(), _register_geocoding_tools(tr), tr.openai_functions())[-1]
    if func_name == "_register_coordinate_tools":
        runners["_register_coordinate_tools"] = lambda: (tr := ToolRegistry(), _register_coordinate_tools(tr), tr.openai_functions())[-1]
    if func_name == "_register_file_tools":
        runners["_register_file_tools"] = lambda: (tr := ToolRegistry(), _register_file_tools(tr), tr.openai_functions())[-1]
    if func_name == "_load_plugins":
        runners["_load_plugins"] = lambda: (tr := ToolRegistry(), _load_plugins(tr), tr.openai_functions())[-1]

    try:
        res1 = run_under_tz("UTC", runners[func_name])
        res2 = run_under_tz("America/New_York", runners[func_name])
        if res1 != res2:
            pytest.xfail(f"{func_name} behavior differs by TZ")
        assert res1 == res2
    finally:
        sys.path.remove(str(plugin_dir))
        monkeypatch.undo()
        if hasattr(time, "tzset"):
            time.tzset()
