import pytest
from unittest.mock import patch
import install_requirements

def test_install_package_unsupported_method():
    with patch('subprocess.run') as mock_run:
        with pytest.raises(ValueError, match="Unsupported installation method: unsupported"):
            install_requirements.install_package('test-pkg', 'unsupported')
        mock_run.assert_not_called()
