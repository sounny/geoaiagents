import sys
import runpy
import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.parametrize("val", [float("nan"), float("inf"), float("-inf"), -0.0])
def test_submit_script_with_numeric_args(val, tmp_path):
    """
    submit.py is a pure execution script with no public functions.
    We test the script execution directly, passing the numeric edge cases
    via mocked sys.argv to ensure it doesn't crash or behave unexpectedly.
    """
    mock_tools = MagicMock()
    with patch.dict('sys.modules', {'tools': mock_tools}):
        with patch('sys.argv', ['submit.py', str(val)]):
            runpy.run_path('submit.py', run_name='__main__')

    mock_tools.submit.assert_called_once()
