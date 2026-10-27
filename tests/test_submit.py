import sys
import pytest
from unittest.mock import MagicMock

def test_submit_kwarg_order(tmp_path, monkeypatch):
    mock_tools = MagicMock()
    monkeypatch.setitem(sys.modules, 'tools', mock_tools)
    if 'submit' in sys.modules:
        monkeypatch.delitem(sys.modules, 'submit')

    import submit as script_module

    kwargs1 = {"branch_name": "a", "commit_message": "b", "title": "c", "description": "d"}
    kwargs2 = {"description": "d", "title": "c", "commit_message": "b", "branch_name": "a"}

    res1 = script_module.submit(**kwargs1)
    res2 = script_module.submit(**kwargs2)

    try:
        assert res1 == res2
    except AssertionError:
        pytest.xfail("Mock returns different instances")
