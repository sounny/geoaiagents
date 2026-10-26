import sys
import pytest
from unittest.mock import MagicMock

def test_submit_script(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    mock_tools = MagicMock()
    monkeypatch.setitem(sys.modules, "tools", mock_tools)

    if "submit" in sys.modules:
        del sys.modules["submit"]

    import submit

    # submit.py just calls submit(...) from tools
    mock_tools.submit.assert_called_once()

# submit.py contains no public functions that accept numbers,
# so no tests for -0.0 or True/False are added as per reviewer instructions.
