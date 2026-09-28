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
        name="duplicate_tool",
        description="A duplicate tool",
        parameters={},
        handler=lambda x: ""
    )
    with pytest.raises(ValueError, match="Tool 'duplicate_tool' is already registered"):
        registry.register_tool(
            name="duplicate_tool",
            description="Another duplicate tool",
            parameters={},
            handler=lambda x: ""
        )

def test_tool_registry_plugin_load_missing_module(caplog, monkeypatch):
    import logging
    registry = ToolRegistry()
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "missing_plugin_module")

    with caplog.at_level(logging.ERROR):
        from tool_registry import _load_plugins
        _load_plugins(registry)

    assert "Failed to load plugin module 'missing_plugin_module':" in caplog.text

def test_tool_registry_plugin_load_missing_register_tools(caplog, monkeypatch, tmp_path):
    import logging
    import sys

    registry = ToolRegistry()

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "invalid_plugin.py"
    plugin_file.write_text("def some_other_function(): pass\n")

    sys.path.insert(0, str(plugin_dir))
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "invalid_plugin")

    try:
        with caplog.at_level(logging.WARNING):
            from tool_registry import _load_plugins
            _load_plugins(registry)

        assert "Plugin module 'invalid_plugin' has no callable register_tools(registry)" in caplog.text
    finally:
        sys.path.remove(str(plugin_dir))
