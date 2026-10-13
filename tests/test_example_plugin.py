import pytest
from plugins.example_plugin import register_tools

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
