import runpy
import warnings
from unittest.mock import patch
import pytest

import sys

# In submit.py there are no functions! It just calls submit() from tools.
# Thus we just test the execution directly using runpy.

@patch.dict('sys.modules', {'tools': __import__('unittest.mock').mock.MagicMock()})
def test_submit_execution_no_warnings(monkeypatch, tmp_path):
    """Test executing the submit.py script directly with warnings as errors."""
    with patch('sys.argv', ['submit.py']):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            runpy.run_path("submit.py", run_name="__main__")
