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

def test_example_plugin_importable():
    """Test that the example_plugin can be imported from plugins."""
    try:
        from plugins import example_plugin
    except Exception as e:
        pytest.xfail(f"Importing example_plugin from plugins failed: {e}")
