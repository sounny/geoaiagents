import pytest
import logging
from tool_registry import create_registry

def test_tool_registry_logging_exception(caplog, monkeypatch):
    registry = create_registry()
    registry.register_tool(
        name="fail_tool",
        description="Test",
        parameters={},
        handler=lambda x: 1/0
    )

    with caplog.at_level(logging.ERROR):
        result = registry.invoke("fail_tool", "{}")

    assert "Error running fail_tool: division by zero" in result

    # Check that exc_info was captured
    for record in caplog.records:
        if record.levelname == "ERROR":
            assert record.exc_info is not None
            assert record.message == "Tool 'fail_tool' failed: division by zero"

def test_tool_registry_plugin_load_exception(caplog, monkeypatch):
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "non_existent_module")

    with caplog.at_level(logging.ERROR):
        registry = create_registry()

    for record in caplog.records:
        if record.levelname == "ERROR":
            assert record.exc_info is not None
            assert "Failed to load plugin module 'non_existent_module'" in record.message
