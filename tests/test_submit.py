"""Tests for submit.py."""

import inspect
import sys
from unittest.mock import MagicMock


def test_submit_public_api(mocker):
    """Test that submit.py defines the expected public API."""
    mock_tools = MagicMock()

    def dummy_submit(*args, **kwargs):
        pass

    mock_tools.submit = dummy_submit
    mocker.patch.dict(sys.modules, {"tools": mock_tools})

    # Force reload if already imported
    if "submit" in sys.modules:
        del sys.modules["submit"]

    import submit

    public_api = {}
    for name in sorted(dir(submit)):
        if not name.startswith("_"):
            obj = getattr(submit, name)
            if inspect.isclass(obj):
                kind = "class"
            elif inspect.isroutine(obj):
                kind = "function"
            else:
                kind = "constant"
            public_api[name] = kind

    expected_api = {
        "submit": "function"
    }

    assert public_api == expected_api
