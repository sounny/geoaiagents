import unittest
from unittest.mock import patch, call, mock_open
import subprocess
import sys
import os

import install_requirements

class TestInstallRequirements(unittest.TestCase):

    @patch('subprocess.run')
    def test_install_package_auto_fallback(self, mock_run):
        error = subprocess.CalledProcessError(1, 'cmd', stderr='error', output='out')
        mock_run.side_effect = [error, subprocess.CompletedProcess(args='cmd', returncode=0)]

        result = install_requirements.install_package_auto('demo-pkg')

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_has_calls([
            call([sys.executable, '-m', 'pip', 'install', '--user', 'demo-pkg'], capture_output=True, text=True, check=True),
            call([sys.executable, '-m', 'pip', 'install', '--break-system-packages', 'demo-pkg'], capture_output=True, text=True, check=True)
        ])

    @patch('subprocess.run')
    def test_install_package_auto_both_fail(self, mock_run):
        error1 = subprocess.CalledProcessError(1, 'cmd', stderr='error', output='out')
        error2 = subprocess.CalledProcessError(1, 'cmd', stderr='error', output='out')
        mock_run.side_effect = [error1, error2]

        result = install_requirements.install_package_auto('demo-pkg')

        self.assertFalse(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch('subprocess.run')
    def test_install_package_normal(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(args='cmd', returncode=0)

        result = install_requirements.install_package('demo-pkg', method='normal')

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [sys.executable, '-m', 'pip', 'install', 'demo-pkg'],
            capture_output=True, text=True, check=True
        )

    @patch('install_requirements.install_package')
    @patch('os.path.exists')
    def test_install_all_requirements(self, mock_exists, mock_install_package):
        mock_exists.return_value = True
        mock_install_package.return_value = True

        file_content = "package1\n# comment\n\npackage2\n"
        with patch('builtins.open', mock_open(read_data=file_content)):
            install_requirements.install_all_requirements('requirements.txt', method='auto')

        self.assertEqual(mock_install_package.call_count, 2)
        mock_install_package.assert_has_calls([
            call('package1', 'auto'),
            call('package2', 'auto')
        ])

if __name__ == '__main__':
    unittest.main()
