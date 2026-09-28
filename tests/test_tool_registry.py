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

def test_tool_registry_duplicate_registration():
    registry = ToolRegistry()
    registry.register_tool(
        name="test_tool",
        description="A test tool",
        parameters={},
        handler=lambda x: "ok"
    )
    with pytest.raises(ValueError, match="Tool 'test_tool' is already registered."):
        registry.register_tool(
            name="test_tool",
            description="Another test tool",
            parameters={},
            handler=lambda x: "ok"
        )

def test_load_plugins_missing_module(monkeypatch, caplog):
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "non_existent_plugin_module")
    registry = ToolRegistry()
    from tool_registry import _load_plugins
    _load_plugins(registry)
    assert "Failed to load plugin module 'non_existent_plugin_module'" in caplog.text

def test_load_plugins_missing_callable(monkeypatch, caplog, tmp_path):
    import sys
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "bad_plugin.py"
    plugin_file.write_text("def wrong_function_name(): pass")

    monkeypatch.syspath_prepend(str(plugin_dir))
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "bad_plugin")

    registry = ToolRegistry()
    from tool_registry import _load_plugins
    _load_plugins(registry)
    assert "Plugin module 'bad_plugin' has no callable register_tools(registry)" in caplog.text
