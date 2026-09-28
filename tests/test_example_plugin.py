import sys
import pytest

def test_example_plugin_import_error(monkeypatch):
    """Test that example_plugin surfaces a clear ImportError when requests is missing."""
    monkeypatch.setitem(sys.modules, "requests", None)
    if 'plugins.example_plugin' in sys.modules:
        del sys.modules['plugins.example_plugin']

    with pytest.raises(ImportError, match="example_plugin requires the 'requests' package"):
        import plugins.example_plugin

def test_example_plugin_import_success(monkeypatch):
    """Test that example_plugin loads successfully when requests is present."""
    if 'plugins.example_plugin' in sys.modules:
        del sys.modules['plugins.example_plugin']

    import plugins.example_plugin
    assert hasattr(plugins.example_plugin, "register_tools")
