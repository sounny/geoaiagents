import sys
from unittest.mock import patch
import install_requirements

@patch('install_requirements.subprocess.run')
def test_install_package_normal(mock_run):
    """Test that install_package with method='normal' uses standard pip install command."""
    mock_run.return_value.returncode = 0

    result = install_requirements.install_package("demo-pkg", method="normal")

    assert result is True
    mock_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "demo-pkg"],
        capture_output=True, text=True, check=True
    )
