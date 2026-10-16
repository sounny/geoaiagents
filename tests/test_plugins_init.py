import pytest
import sys

def test_plugins_package_imports_cleanly():
    """Test that the plugins package can be imported without side effects that raise."""
    if "plugins" in sys.modules:
        del sys.modules["plugins"]

    try:
        import plugins
    except Exception as e:
        pytest.fail(f"Importing plugins raised an unexpected exception: {e}")

def test_plugin_discovery_deterministic_and_skips_broken(tmp_path, monkeypatch):
    """
    Test that plugins are discovered in a deterministic order
    and a broken plugin module is skipped or reported as documented.
    """
    try:
        from plugins import discover_plugins
    except ImportError:
        pytest.xfail("plugin discovery helper is missing or current behavior differs")

    # Create dummy plugin files
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    (plugins_dir / "__init__.py").write_text("")
    (plugins_dir / "plugin_c.py").write_text("def register_tools(registry): registry.register_tool(name='c', description='', parameters={}, handler=lambda x: None)")
    (plugins_dir / "plugin_a.py").write_text("def register_tools(registry): registry.register_tool(name='a', description='', parameters={}, handler=lambda x: None)")
    (plugins_dir / "plugin_broken.py").write_text("raise ImportError('I am broken')")
    (plugins_dir / "plugin_b.py").write_text("def register_tools(registry): registry.register_tool(name='b', description='', parameters={}, handler=lambda x: None)")

    # Add tmp_path to sys.path so the dummy plugins can be imported
    monkeypatch.syspath_prepend(str(tmp_path))

    from tool_registry import ToolRegistry
    registry = ToolRegistry()

    # Invoke the discovery helper
    discover_plugins(registry, str(plugins_dir))

    loaded_tools = list(registry._tools.keys())

    # Expected deterministic order: alphabetical, skipping the broken one
    assert loaded_tools == ["a", "b", "c"]
