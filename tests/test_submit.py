import sys
import time
from unittest.mock import MagicMock
import pytest

def make_nested(depth, kind):
    curr = kind()
    head = curr
    for i in range(depth):
        next_curr = kind()
        if kind == list:
            curr.append(next_curr)
            curr = next_curr
        else:
            curr['key'] = next_curr
            curr = next_curr
    return head

def test_submit_nested_dict(tmp_path):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools
    if 'submit' in sys.modules: del sys.modules['submit']

    import submit as script_module
    arg = make_nested(200, dict)

    t0 = time.time()
    script_module.submit(branch_name=arg, commit_message="msg", title="title", description="desc")
    t1 = time.time()
    assert t1 - t0 < 1.0

    mock_tools.submit.assert_called_with(branch_name=arg, commit_message="msg", title="title", description="desc")

def test_submit_nested_list(tmp_path):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools
    if 'submit' in sys.modules: del sys.modules['submit']

    import submit as script_module
    arg = make_nested(200, list)

    t0 = time.time()
    script_module.submit(branch_name=arg, commit_message="msg", title="title", description="desc")
    t1 = time.time()
    assert t1 - t0 < 1.0

    mock_tools.submit.assert_called_with(branch_name=arg, commit_message="msg", title="title", description="desc")

@pytest.mark.xfail(raises=RecursionError, strict=False, reason="RecursionError on self-referencing list with mock equality in some python versions")
def test_submit_recursive_list(tmp_path):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools
    if 'submit' in sys.modules: del sys.modules['submit']

    import submit as script_module
    arg = []
    arg.append(arg)

    t0 = time.time()
    script_module.submit(branch_name=arg, commit_message="msg", title="title", description="desc")
    t1 = time.time()
    assert t1 - t0 < 1.0

    mock_tools.submit.assert_called_with(branch_name=arg, commit_message="msg", title="title", description="desc")
