"""Tests for submit.py script."""

import builtins
import runpy
import sys
from unittest.mock import MagicMock, patch

def test_submit_script_execution():
    """Test submit.py execution with mock tools.submit."""
    mock_submit = MagicMock()
    mock_tools_module = MagicMock()
    mock_tools_module.submit = mock_submit

    with patch.dict(sys.modules, {'tools': mock_tools_module}):
        runpy.run_path('submit.py', run_name='__main__')

    mock_submit.assert_called_once()
    called_kwargs = mock_submit.call_args.kwargs
    assert called_kwargs.get("branch_name") == "jules-2495290425968265034-2865bb1d"
    assert called_kwargs.get("commit_message") == "Fix load_csv empty table on missing headers"
    assert called_kwargs.get("title") == "Fix load_csv empty table on missing headers"
    assert called_kwargs.get("description") == "Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data."

def test_submit_script_with_special_characters(tmp_path):
    """Test submit.py execution with special characters in its text fields."""
    # Since submit.py doesn't accept input dynamically, we simulate modifying the file
    # to ensure the submission logic itself handles the text properly without crashing.
    original_file = "submit.py"
    with open(original_file, 'r', encoding='utf-8') as f:
        code = f.read()

    special_text = "résumé 漢字 🚀"

    modified_code = code.replace("Fix load_csv empty table on missing headers", special_text)
    modified_code = modified_code.replace("Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data.", special_text)

    test_script_path = tmp_path / "submit_special.py"
    test_script_path.write_text(modified_code, encoding="utf-8")

    mock_submit = MagicMock()
    mock_tools_module = MagicMock()
    mock_tools_module.submit = mock_submit

    with patch.dict(sys.modules, {'tools': mock_tools_module}):
        runpy.run_path(str(test_script_path), run_name='__main__')

    mock_submit.assert_called_once()
    called_kwargs = mock_submit.call_args.kwargs
    assert called_kwargs.get('commit_message') == special_text
    assert called_kwargs.get('title') == special_text
    assert called_kwargs.get('description') == special_text
