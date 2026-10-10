import pytest
import os
from install_requirements import read_requirements

def test_read_requirements(tmp_path):
    # Create a temporary requirements.txt file
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("\n".join([
        "# comment",
        "",
        "numpy",
        "  # x",
        "requests==2.0"
    ]))

    # Assert that read_requirements correctly parses it
    assert read_requirements(str(req_file)) == ["numpy", "requests==2.0"]
