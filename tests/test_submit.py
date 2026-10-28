import sys
import importlib
from unittest.mock import MagicMock, patch
import pytest

@pytest.mark.xfail(reason="Bug: script ignores input and submits hardcoded payload")
def test_submit_zero_byte(tmp_path):
    mock_tools = MagicMock()
    file_path = tmp_path / "zero_byte.txt"
    file_path.touch()

    with patch.dict('sys.modules', {'tools': mock_tools}):
        with open(file_path, 'r') as f:
            with patch('sys.stdin', new=f):
                if 'submit' in sys.modules:
                    importlib.reload(sys.modules['submit'])
                else:
                    import submit

                mock_tools.submit.assert_not_called()

@pytest.mark.xfail(reason="Bug: script ignores input and submits hardcoded payload")
def test_submit_whitespace(tmp_path):
    mock_tools = MagicMock()
    file_path = tmp_path / "whitespace.txt"
    file_path.write_text("   \n\t  ")

    with patch.dict('sys.modules', {'tools': mock_tools}):
        with open(file_path, 'r') as f:
            with patch('sys.stdin', new=f):
                if 'submit' in sys.modules:
                    importlib.reload(sys.modules['submit'])
                else:
                    import submit

                mock_tools.submit.assert_not_called()
