import os
import sys
import pytest
from unittest.mock import MagicMock

def test_submit_script_write_readonly(tmp_path):
    if sys.platform == "win32":
        pytest.skip("Test requires POSIX chmod for read-only directories")
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("Root user bypasses read-only directory permissions")

    test_file = tmp_path / "mock_log.txt"
    os.chmod(tmp_path, 0o555)

    mock_tools = MagicMock()

    def side_effect_submit(*args, **kwargs):
        with open(test_file, "w") as f:
            f.write("called")

    mock_tools.submit.side_effect = side_effect_submit

    original_tools = sys.modules.get('tools')
    sys.modules['tools'] = mock_tools

    try:
        if 'submit' in sys.modules:
            del sys.modules['submit']
        try:
            import submit
            res = None
        except Exception as e:
            res = e
    finally:
        if original_tools is not None:
            sys.modules['tools'] = original_tools
        else:
            sys.modules.pop('tools', None)

    if isinstance(res, PermissionError):
        pytest.xfail("PermissionError when writing to a read-only directory looks like a bug")
    elif res is not None:
        raise res
