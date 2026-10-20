import pytest
import plugins.example_plugin
from plugins.example_plugin import register_tools
from tool_registry import ToolRegistry

class MockRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, description, parameters, handler):
        self.tools[name] = handler


def test_ping_api_unknown():
    registry = MockRegistry()
    register_tools(registry)
    handler = registry.tools["ping_api"]
    result = handler({})
    assert "unknown" in result
    assert "plugin-ok" in result

def test_ping_api_demo():
    registry = MockRegistry()
    register_tools(registry)
    handler = registry.tools["ping_api"]
    result = handler({"endpoint": "demo"})
    assert "demo" in result
    assert "plugin-ok" in result

def test_register_tools_fresh_registry():
    registry = ToolRegistry()
    register_tools(registry)
    assert registry.has_tool("ping_api")
    funcs = registry.openai_functions()
    assert any(f["name"] == "ping_api" for f in funcs)

@pytest.mark.xfail(reason="Unknown hooks raise AttributeError, but they should be safe.")
def test_unknown_hook_safe():
    plugins.example_plugin.unknown_hook()
