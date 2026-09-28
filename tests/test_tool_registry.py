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
    registry.register_tool(name="test_tool", description="test", parameters={}, handler=lambda x: "")
    with pytest.raises(ValueError, match="Tool 'test_tool' is already registered"):
        registry.register_tool(name="test_tool", description="test2", parameters={}, handler=lambda x: "")

def test_load_plugins_missing_module(monkeypatch, caplog):
    registry = ToolRegistry()
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "plugins.non_existent_plugin")

    from tool_registry import _load_plugins
    _load_plugins(registry)

    assert "Failed to load plugin module 'plugins.non_existent_plugin'" in caplog.text

def test_load_plugins_missing_callable(monkeypatch, caplog, tmp_path):
    # Create a fake module dynamically to avoid file creation if possible,
    # but since it's easier, we will mock importlib.import_module

    import importlib

    class FakeModule:
        pass

    original_import_module = importlib.import_module
    def mock_import_module(name):
        if name == "plugins.no_callable_plugin":
            return FakeModule()
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", mock_import_module)
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "plugins.no_callable_plugin")

    registry = ToolRegistry()
    from tool_registry import _load_plugins
    _load_plugins(registry)

    assert "Plugin module 'plugins.no_callable_plugin' has no callable register_tools(registry)" in caplog.text
