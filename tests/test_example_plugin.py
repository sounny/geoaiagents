import pytest
from tool_registry import ToolRegistry
from plugins.example_plugin import register_tools

def test_example_plugin_registration_and_invocation():
    """Test that example_plugin can be registered and invoked correctly."""
    registry = ToolRegistry()

    # Register the tools from the plugin
    register_tools(registry)

    # Verify the tool was registered
    assert registry.has_tool('ping_api') is True

    # Invoke the tool
    result = registry.invoke('ping_api', {'endpoint': 'demo'})

    # Verify the result
    assert "demo" in result
    assert "plugin-ok" in result
    assert "| endpoint | status |" in result
