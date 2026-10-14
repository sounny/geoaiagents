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

def test_load_plugins_valid_and_broken(tmp_path, monkeypatch):
    """Test loading plugins from a temporary plugins directory with one valid and one broken plugin."""
    import sys
    from tool_registry import _load_plugins

    # Create valid plugin
    valid_plugin_file = tmp_path / "test_valid_plugin.py"
    valid_plugin_file.write_text(
        "def register_tools(registry):\n"
        "    registry.register_tool(\n"
        "        name='valid_test_tool',\n"
        "        description='A valid test tool',\n"
        "        parameters={}, \n"
        "        handler=lambda args: 'valid'\n"
        "    )\n"
    )

    # Create broken plugin
    broken_plugin_file = tmp_path / "test_broken_plugin.py"
    broken_plugin_file.write_text(
        "raise ImportError('Simulated broken plugin')\n"
    )

    # Add tmp_path to sys.path so modules can be imported
    monkeypatch.syspath_prepend(str(tmp_path))

    # Set GEOAI_PLUGIN_MODULES to load both plugins
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "test_valid_plugin, test_broken_plugin")

    # Create registry and load plugins
    registry = ToolRegistry()
    _load_plugins(registry)

    # Check that the valid tool was registered
    assert registry.has_tool("valid_test_tool") is True

    # Clean up sys.modules
    sys.modules.pop("test_valid_plugin", None)
    sys.modules.pop("test_broken_plugin", None)
