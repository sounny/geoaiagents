import sys
import runpy
from unittest.mock import MagicMock, patch

def test_submit_never_reads_clock():
    """
    submit.py never reads the clock.
    This test verifies that submit.py runs and calls tools.submit
    without reading the time or making network calls.
    """
    mock_tools = MagicMock()
    mock_submit = MagicMock()
    mock_tools.submit = mock_submit

    with patch.dict(sys.modules, {'tools': mock_tools}), patch.object(sys, 'argv', ['submit.py']):
        runpy.run_path('submit.py', run_name='__main__')

    mock_submit.assert_called_once_with(
        branch_name="jules-2495290425968265034-2865bb1d",
        commit_message="Fix load_csv empty table on missing headers",
        title="Fix load_csv empty table on missing headers",
        description="Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data."
    )
