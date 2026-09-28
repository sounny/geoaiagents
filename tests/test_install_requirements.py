import os
import pytest
from install_requirements import read_requirements

def test_read_requirements_path_traversal_relative():
    with pytest.raises(ValueError, match="Path traversal detected: path outside repository"):
        read_requirements("../requirements.txt")

def test_read_requirements_path_traversal_absolute():
    with pytest.raises(ValueError, match="Path traversal detected: path outside repository"):
        read_requirements("/tmp/requirements.txt")

def test_read_requirements_missing_file():
    # Inside repo, but missing
    assert read_requirements("nonexistent_reqs.txt") == []

def test_read_requirements_valid_file(tmp_path):
    # tmp_path is outside the repo typically, but let's test creating a file inside the repo
    repo_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    test_file_path = os.path.join(repo_root, "test_valid_reqs.txt")

    with open(test_file_path, "w") as f:
        f.write("pytest\nrequests\n# this is a comment\n\npytest-mock\n")

    try:
        reqs = read_requirements(test_file_path)
        assert reqs == ["pytest", "requests", "pytest-mock"]
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
