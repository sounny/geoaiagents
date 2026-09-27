import pytest
import tool_registry
import logging
import os
import geocode

def test_tool_registry_exception_logging(mocker):
    registry = tool_registry.create_registry()

    def failing_handler(args):
        raise ValueError("Simulated tool failure")

    registry.register_tool(
        name="failing_tool",
        description="Fails unconditionally",
        parameters={},
        handler=failing_handler
    )

    mock_logging = mocker.patch('tool_registry.logging.exception')

    result = registry.invoke("failing_tool", {})

    assert "Error running failing_tool: Simulated tool failure" in result
    mock_logging.assert_called_once()
    assert mock_logging.call_args[0][0] == "Tool '%s' failed: %s"
    assert mock_logging.call_args[0][1] == "failing_tool"

def test_plugin_loading_exception_logging(mocker, monkeypatch):
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "plugins.nonexistent_plugin")

    mock_logging = mocker.patch('tool_registry.logging.exception')

    registry = tool_registry.ToolRegistry()
    tool_registry._load_plugins(registry)

    mock_logging.assert_called_once()
    assert "Failed to load plugin module '%s': %s" in mock_logging.call_args[0][0]
