import sys
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from install_requirements import read_requirements, install_package

def test_read_requirements_trailing_space_stripping_and_pin_keeping():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('requests==2.32.0   \n\n# comment\n numpy>=1.26\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['requests==2.32.0', 'numpy>=1.26']
    finally:
        os.remove(temp_name)

def test_read_requirements_keeps_flask_and_drops_hash_comment():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('flask==2.0.0 # hash comment\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['flask==2.0.0']
    finally:
        os.remove(temp_name)

def test_install_package_success():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        result = install_package('dummy_package', method='normal')

        assert result is True
        mock_run.assert_called_once()

def test_install_package_failure():
    with patch('subprocess.run') as mock_run:
        mock_error = subprocess.CalledProcessError(1, cmd=['pip'], stderr='Mocked error message')
        mock_run.side_effect = mock_error

        with patch('builtins.print') as mock_print:
            result = install_package('dummy_package', method='normal')

            assert result is False
            mock_run.assert_called_once()

            # Check if error message is printed
            mock_print.assert_any_call('Error details: Mocked error message')
