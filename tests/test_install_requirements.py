import pytest
from unittest.mock import patch
import install_requirements

def test_missing_requirements_path_fails_clearly(capsys):
    """Test that missing requirements file path fails clearly and doesn't invoke pip."""
    with patch('subprocess.run') as mock_run:
        install_requirements.install_all_requirements(None)

        # Pip should not be invoked
        mock_run.assert_not_called()

        captured = capsys.readouterr()
        # Verify a clear error is shown rather than uncaught traceback
        assert "Error:" in captured.out
        # Or if it prints to stderr:
        # assert "Error:" in captured.err or "Error:" in captured.out
