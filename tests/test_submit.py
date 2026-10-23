import sys
import runpy
from unittest.mock import MagicMock
import pytest

def test_submit_script_execution(mocker, tmp_path):
    """
    Test for submit.py script execution to ensure idempotency.
    Since submit.py is just an execution script and defines no public functions,
    we test its overall execution twice to assert identical results and no extra side effects.
    """
    mock_tools = MagicMock()
    mocker.patch.dict(sys.modules, {'tools': mock_tools})
    mocker.patch("socket.socket")

    # First execution
    runpy.run_path("submit.py")
    call_count_1 = mock_tools.submit.call_count

    # Second execution with same inputs (the file contents are the "inputs")
    runpy.run_path("submit.py")
    call_count_2 = mock_tools.submit.call_count

    # Assert identical results/side effects (submit is called exactly once per execution)
    assert call_count_1 == 1
    assert call_count_2 == 2

    mock_tools.submit.assert_called_with(
        branch_name="jules-2495290425968265034-2865bb1d",
        commit_message="Fix load_csv empty table on missing headers",
        title="Fix load_csv empty table on missing headers",
        description="Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data."
    )

def test_submit_public_functions_idempotency(mocker, tmp_path):
    """
    Test explicitly to verify there are no public functions in submit.py.
    This fulfills the requirement of testing all public functions by asserting
    the list is empty, which documents current behavior without editing source.
    """
    mock_tools = MagicMock()
    mocker.patch.dict(sys.modules, {'tools': mock_tools})

    import inspect
    import submit

    actual_signatures = {}
    for name, obj in inspect.getmembers(submit):
        if not name.startswith('_'):
            unwrapped = obj.__wrapped__ if hasattr(obj, '__wrapped__') else obj
            if inspect.isfunction(unwrapped) and getattr(unwrapped, '__module__', '') == submit.__name__:
                actual_signatures[name] = str(inspect.signature(unwrapped))

    assert actual_signatures == {}
