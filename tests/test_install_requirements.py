import unittest
from unittest.mock import patch, call
import sys
import install_requirements

class TestInstallRequirements(unittest.TestCase):

    @patch('subprocess.run')
    def test_install_package_user(self, mock_run):
        # Configure mock
        mock_run.return_value.returncode = 0

        # Call function
        result = install_requirements.install_package("demo-pkg", method="user")

        # Assertions
        self.assertTrue(result)

        expected_cmd = [sys.executable, "-m", "pip", "install", "--user", "demo-pkg"]
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True, check=True)

if __name__ == '__main__':
    unittest.main()
