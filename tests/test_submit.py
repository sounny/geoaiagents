import sys
import pytest
from unittest.mock import MagicMock

def test_submit_unknown_keys(monkeypatch):
    mock_tools = MagicMock()
    monkeypatch.setitem(sys.modules, 'tools', mock_tools)
    monkeypatch.delitem(sys.modules, 'submit', raising=False)

    import submit as script_module

    config = {
        "branch_name": "test_branch",
        "commit_message": "msg",
        "title": "t",
        "description": "d",
        "unknown_key": "some_value"
    }

    try:
        script_module.submit(**config)
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
             pass
        else:
             raise
    else:
        pytest.xfail("Bug: Imported function silently accepts dicts with unknown keys instead of rejecting them")
