import os
import pytest
from install_requirements import read_requirements

def test_read_requirements_skips_comments_and_blanks(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("# comment\n\nnumpy\n  # x\nrequests==2.0\n")
    result = read_requirements(str(req_file))
    assert result == ['numpy', 'requests==2.0']

def test_read_requirements_preserves_version_pins(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("# comment\n\ngeopy>=2.0\nopenai==1.0.0\n")
    result = read_requirements(str(req_file))
    assert result == ['geopy>=2.0', 'openai==1.0.0']

def test_read_requirements_missing_file():
    result = read_requirements('/tmp/definitely-missing-reqs-9f3abc.txt')
    assert result == []
