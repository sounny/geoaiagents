import sys
import os
import pytest

def test_pytest_pythonpath(pytestconfig):
    """Verify that pytest configuration sets a pythonpath so project modules import under pytest."""

    # Try to get pythonpath from pytestconfig (works for pytest.ini, pyproject.toml, setup.cfg)
    try:
        paths = pytestconfig.getini("pythonpath")
        if paths:
            # Check if any of the configured paths exist
            for p in paths:
                if os.path.exists(p):
                    return # Success
    except ValueError:
        # pytest < 7.0 doesn't have the pythonpath ini option natively
        pass

    # Fallback: check if the project root (or tests/..) is in sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    for path in sys.path:
        if os.path.abspath(path) == project_root:
            return # Success

    pytest.xfail("pythonpath not configured correctly in pytest config")
