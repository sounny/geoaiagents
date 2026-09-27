import pytest
from unittest.mock import patch, MagicMock
import tool_registry
import os

def test_invoke_exception_logging():
    registry = tool_registry.ToolRegistry()

    def failing_handler(args):
        raise ValueError("Test error")

    registry.register_tool(
        name="test_tool",
        description="test",
        parameters={},
        handler=failing_handler
    )

    with patch("logging.exception") as mock_logging:
        result = registry.invoke("test_tool", {})
        assert "Error running test_tool: Test error" in result
        mock_logging.assert_called_once()
        assert "Tool '%s' failed: %s" in mock_logging.call_args[0][0]
        assert mock_logging.call_args[0][1] == "test_tool"

def test_load_plugins_exception_logging():
    registry = tool_registry.ToolRegistry()

    with patch.dict(os.environ, {"GEOAI_PLUGIN_MODULES": "non_existent_module"}):
        with patch("logging.exception") as mock_logging:
            tool_registry._load_plugins(registry)
            mock_logging.assert_called_once()
            assert "Failed to load plugin module '%s': %s" in mock_logging.call_args[0][0]
            assert mock_logging.call_args[0][1] == "non_existent_module"

def test_load_plugins_no_register_tools_logging():
    registry = tool_registry.ToolRegistry()

    # Create a dummy module without register_tools
    import sys
    import types
    dummy_module = types.ModuleType("dummy_plugin")
    sys.modules["dummy_plugin"] = dummy_module

    with patch.dict(os.environ, {"GEOAI_PLUGIN_MODULES": "dummy_plugin"}):
        with patch("logging.warning") as mock_logging:
            tool_registry._load_plugins(registry)
            mock_logging.assert_called_once()
            assert "Plugin module '%s' has no callable register_tools(registry)" in mock_logging.call_args[0][0]
            assert mock_logging.call_args[0][1] == "dummy_plugin"
