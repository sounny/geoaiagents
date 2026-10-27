import sys
from unittest.mock import MagicMock

def test_submit_execution(monkeypatch, tmp_path):
    mock_tools = MagicMock()
    mock_submit = MagicMock()
    mock_submit.return_value = {"status": "success"}
    mock_tools.submit = mock_submit

    monkeypatch.setitem(sys.modules, 'tools', mock_tools)
    monkeypatch.delitem(sys.modules, 'submit', raising=False)

    import submit

    mock_submit.assert_called_once_with(
        branch_name="jules-2495290425968265034-2865bb1d",
        commit_message="Fix load_csv empty table on missing headers",
        title="Fix load_csv empty table on missing headers",
        description="Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data."
    )
