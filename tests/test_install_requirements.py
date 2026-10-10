import pytest
from unittest.mock import patch
import os
import sys

# Add parent directory to path to import install_requirements
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from install_requirements import install_all_requirements

def test_install_all_requirements_skips_comments_and_blank_lines(tmp_path):
    req_file = tmp_path / "reqs.txt"
    req_file.write_text("pkg1\n\n# comment\npkg2\n   \n# another comment\n")

    with patch("install_requirements.install_package") as mock_install:
        mock_install.return_value = True
        install_all_requirements(str(req_file))

        assert mock_install.call_count == 2
        mock_install.assert_any_call("pkg1", "auto")
        mock_install.assert_any_call("pkg2", "auto")
