import sys
from unittest.mock import MagicMock, patch
import random
import runpy

def test_submit_idempotent():
    # Mock network calls safely using runpy to execute the script in a fresh namespace.
    # The submit.py script relies on a global `tools` module.
    mock_tools = MagicMock()

    # We patch sys.modules so that when runpy executes submit.py,
    # the internal 'import tools' picks up our mock.
    # We also patch sys.argv to avoid inheriting pytest's arguments,
    # as runpy execution passes sys.argv down.
    with patch.dict('sys.modules', {'tools': mock_tools}), patch.object(sys, 'argv', ['submit.py']):

        # Execute script first time
        random.seed(42)
        runpy.run_path("submit.py", run_name="__main__")

        # Execute script second time
        random.seed(42)
        runpy.run_path("submit.py", run_name="__main__")

        # Verify the mock was called exactly twice (once per run)
        assert mock_tools.submit.call_count == 2

        # Check identical outcomes/outputs
        call1 = mock_tools.submit.call_args_list[0]
        call2 = mock_tools.submit.call_args_list[1]

        assert call1 == call2, "Outputs (arguments to tools.submit) are not identical"
