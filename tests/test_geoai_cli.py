import pytest
import sys
from geoai_cli import main

def test_cli_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["geoai_cli.py", "--help"])
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0

    captured = capsys.readouterr()

    subcommands = [
        "list-tools",
        "run-tool",
        "geocode",
        "reverse",
        "dms",
        "distance",
        "boundaries",
        "chat"
    ]
    for cmd in subcommands:
        assert cmd in captured.out
