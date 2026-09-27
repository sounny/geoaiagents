import pytest
import os
import sys

# To ensure the directory contains what we need and is reachable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tool_registry import create_registry

def test_registry_contains_tools():
    """Verify tool_registry correctly registers tools."""
    registry = create_registry()
    assert registry.has_tool("geocode_locations")
    assert registry.has_tool("convert_dd_to_dms")
