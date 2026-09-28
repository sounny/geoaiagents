import pytest
from tool_registry import ToolRegistry
from plugins.example_plugin import register_tools

def test_example_plugin_register_tools_idempotent():
    registry = ToolRegistry()

    # First call should register the tool
    register_tools(registry)
    assert registry.has_tool("ping_api")

    # Second call should not crash (idempotency check)
    try:
        register_tools(registry)
    except ValueError:
        pytest.fail("register_tools raised ValueError unexpectedly on second call")

def test_example_plugin_ping_api():
    registry = ToolRegistry()
    register_tools(registry)

    # The tool is wrapped in the registry invoke method
    result = registry.invoke("ping_api", {"endpoint": "test.com"})

    assert "test.com" in result
    assert "plugin-ok" in result

def test_example_plugin_ping_api_default_endpoint():
    registry = ToolRegistry()
    register_tools(registry)

    result = registry.invoke("ping_api", {})

    assert "unknown" in result
    assert "plugin-ok" in result
