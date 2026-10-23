import sys
import runpy
import pytest
from unittest.mock import patch, MagicMock

def test_submit_script_execution():
    """Test that submit.py correctly calls tools.submit with expected arguments."""
    mock_tools = MagicMock()
    with patch.dict(sys.modules, {'tools': mock_tools}):
        with patch('sys.argv', ['submit.py']):
            runpy.run_path('submit.py', run_name='__main__')

            mock_tools.submit.assert_called_once()

            _, kwargs = mock_tools.submit.call_args
            assert "branch_name" in kwargs
            assert "commit_message" in kwargs
            assert "title" in kwargs
            assert "description" in kwargs
