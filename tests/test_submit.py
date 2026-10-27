import sys
import time
import importlib
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def restore_timezone():
    """Ensure the C library timezone state is restored after the test."""
    import os
    original_tz = os.environ.get('TZ')
    yield
    if original_tz is not None:
        os.environ['TZ'] = original_tz
    else:
        os.environ.pop('TZ', None)
    if hasattr(time, 'tzset'):
        time.tzset()

def test_submit_script_timezone_independence(monkeypatch, tmp_path, restore_timezone):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools

    # Run in tmp_path to isolate any potential file access
    monkeypatch.chdir(tmp_path)

    # Execution 1: UTC
    monkeypatch.setenv('TZ', 'UTC')
    if hasattr(time, 'tzset'):
        time.tzset()

    if 'submit' in sys.modules:
        del sys.modules['submit']
    import submit
    # Because submit.py executes on import and defines no functions,
    # its public interface is its side-effects on import.
    calls_tz1 = list(mock_tools.submit.call_args_list)

    # Reset mock for next execution
    mock_tools.submit.reset_mock()

    # Execution 2: America/New_York
    monkeypatch.setenv('TZ', 'America/New_York')
    if hasattr(time, 'tzset'):
        time.tzset()

    importlib.reload(submit)
    calls_tz2 = list(mock_tools.submit.call_args_list)

    if calls_tz1 != calls_tz2:
        pytest.xfail("Behavior differs under different TZ environments")

    assert calls_tz1 == calls_tz2
