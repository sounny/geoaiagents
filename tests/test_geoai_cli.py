import sys
import pytest
from unittest.mock import patch
from geoai_cli import main

def test_main_no_subcommand(capsys):
    """Running without a subcommand should print usage to stderr and return 2."""
    with patch.object(sys, "argv", ["geoai_cli.py"]):
        assert main() == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "usage:" in captured.err

def test_main_invalid_subcommand(capsys):
    """Running with an invalid subcommand should exit with status 2 and print usage to stderr."""
    with patch.object(sys, "argv", ["geoai_cli.py", "invalid_command"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "usage:" in captured.err
