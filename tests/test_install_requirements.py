import unittest
import unittest.mock
import install_requirements
import subprocess
import sys

class TestInstallRequirements(unittest.TestCase):
    @unittest.mock.patch('subprocess.run')
    def test_install_package_system(self, mock_run):
        # Configure the mock to simulate a successful installation
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='success', stderr='')

        result = install_requirements.install_package('demo-pkg', method='system')

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--break-system-packages", "demo-pkg"],
            capture_output=True, text=True, check=True
        )

if __name__ == '__main__':
    unittest.main()
