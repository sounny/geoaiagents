import pytest
import logging
from tool_registry import ToolRegistry, _register_builtin_tools, _load_plugins

def test_tool_registry_logging_error_exception(caplog):
    registry = ToolRegistry()
    _register_builtin_tools(registry)

    def failing_handler(args):
        raise ValueError("Intentional failure")

    registry.register_tool(
        name="failing_tool",
        description="A tool that fails",
        parameters={},
        handler=failing_handler
    )

    with caplog.at_level(logging.ERROR):
        result = registry.invoke("failing_tool", {})

    assert "Tool 'failing_tool' failed: Intentional failure" in caplog.text

    # Check if exc_info was used (which prints traceback in tests)
    for record in caplog.records:
        if "failed:" in record.message:
            assert record.exc_info is not None, "Error should be logged with exc_info=True"

def test_tool_registry_plugin_load_logging_warning_exception(caplog, monkeypatch):
    registry = ToolRegistry()
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "non_existent_module_for_test")

    with caplog.at_level(logging.WARNING):
        _load_plugins(registry)

    assert "Failed to load plugin module 'non_existent_module_for_test'" in caplog.text

    # Check if exc_info was used (which prints traceback in tests)
    found_exc_info = False
    for record in caplog.records:
        if "Failed to load plugin module" in record.message:
            assert record.exc_info is not None, "Warning should be logged with exc_info=True"
            found_exc_info = True
    assert found_exc_info
