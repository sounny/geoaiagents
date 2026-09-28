from plugins.example_plugin import register_tools
from tool_registry import ToolRegistry

def test_example_plugin_registers_tools():
    registry = ToolRegistry()
    register_tools(registry)

    assert registry.has_tool("ping_api")

    result = registry.invoke("ping_api", {"endpoint": "test-endpoint"})
    assert "test-endpoint" in result
    assert "plugin-ok" in result
