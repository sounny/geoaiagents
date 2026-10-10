import os
import sys
import pytest
from unittest import mock
import subprocess

# Import the module to test
import install_requirements

def test_missing_requirements_file(capsys):
    """Test that a missing requirements file exits with 1 and prints an error."""
    with pytest.raises(SystemExit) as excinfo:
        install_requirements.read_requirements("nonexistent_file.txt")

    assert excinfo.value.code == 1

    # Check stderr
    captured = capsys.readouterr()
    assert "Error: nonexistent_file.txt not found!" in captured.err

def test_empty_requirements_file(tmp_path, capsys):
    """Test handling of an empty requirements file."""
    empty_req = tmp_path / "empty_req.txt"
    empty_req.write_text("")

    install_requirements.install_all_requirements(str(empty_req))

    captured = capsys.readouterr()
    assert "No requirements found!" in captured.out

def test_dry_run_auto(tmp_path, capsys, mocker):
    """Test that dry-run mode doesn't execute subprocesses."""
    mock_run = mocker.patch("subprocess.run")

    req_file = tmp_path / "reqs.txt"
    req_file.write_text("testpkg>=1.0\n")

    install_requirements.install_all_requirements(str(req_file), method="auto", dry_run=True)

    mock_run.assert_not_called()

    captured = capsys.readouterr()
    assert "DRY RUN: Would execute:" in captured.out
    assert "✓ Successfully installed testpkg>=1.0 (dry-run)" in captured.out

def test_dry_run_system(tmp_path, capsys, mocker):
    """Test that dry-run mode works with explicit method."""
    mock_run = mocker.patch("subprocess.run")

    req_file = tmp_path / "reqs.txt"
    req_file.write_text("testpkg>=1.0\n")

    install_requirements.install_all_requirements(str(req_file), method="system", dry_run=True)

    mock_run.assert_not_called()

    captured = capsys.readouterr()
    assert "DRY RUN: Would execute:" in captured.out
    assert "✓ Successfully installed testpkg>=1.0 (dry-run)" in captured.out
