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
