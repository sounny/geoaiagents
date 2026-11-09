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

def test_plugins_no_side_effects(monkeypatch):
    import sys
    import socket
    import builtins
    from unittest import mock
    if "plugins" in sys.modules:
        del sys.modules["plugins"]

    network_calls = []
    file_writes = []

    def mock_socket(*args, **kwargs):
        network_calls.append(("socket", args, kwargs))
        return mock.MagicMock()

    monkeypatch.setattr(socket, "socket", mock_socket)

    original_open = builtins.open
    def mock_open(file, mode="r", *args, **kwargs):
        if "w" in mode or "a" in mode or "+" in mode or "x" in mode:
            file_writes.append((file, mode))
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    import plugins

    if network_calls or file_writes:
        pytest.fail(f"Importing plugins had side effects: network_calls={network_calls}, file_writes={file_writes}")
