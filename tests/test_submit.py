import sys
import pytest
from unittest.mock import MagicMock

def test_submit_str_and_bytes(tmp_path):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools

    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy")

    try:
        import submit as script_module

        str_kwargs = {
            "branch_name": "test-branch",
            "commit_message": "test msg",
            "title": "test title",
            "description": "test desc"
        }

        script_module.submit(**str_kwargs)
        call_args_str = mock_tools.submit.call_args

        # Test baseline with string passes
        assert type(call_args_str.kwargs['branch_name']) is str
        assert type(call_args_str.kwargs['commit_message']) is str
        assert type(call_args_str.kwargs['title']) is str
        assert type(call_args_str.kwargs['description']) is str

    finally:
        del sys.modules['tools']

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="Missing coercion to str in submit.py")
def test_submit_str_and_bytes_bug(tmp_path):
    mock_tools = MagicMock()
    sys.modules['tools'] = mock_tools

    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy")

    try:
        if 'submit' in sys.modules:
            del sys.modules['submit']
        import submit as script_module

        bytes_kwargs = {
            "branch_name": b"test-branch",
            "commit_message": b"test msg",
            "title": b"test title",
            "description": b"test desc"
        }

        script_module.submit(**bytes_kwargs)
        call_args_bytes = mock_tools.submit.call_args

        # This will fail and correctly raise AssertionError which is caught by xfail
        assert type(call_args_bytes.kwargs['branch_name']) is str
        assert type(call_args_bytes.kwargs['commit_message']) is str
        assert type(call_args_bytes.kwargs['title']) is str
        assert type(call_args_bytes.kwargs['description']) is str

    finally:
        del sys.modules['tools']
