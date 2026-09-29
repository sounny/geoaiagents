import pytest
import os
import tempfile
from install_requirements import read_requirements

def test_read_requirements_filtering():
    """Test read_requirements on a file with blank lines, comments, and valid packages."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("\n\n# comment 1\nrequests==2.31.0\n# comment 2\n\n")
        temp_path = f.name

    try:
        reqs = read_requirements(temp_path)
        assert reqs == ['requests==2.31.0'], "Expected only the valid package string to be parsed"
    finally:
        os.remove(temp_path)
