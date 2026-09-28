import sys
import pytest
from geoai_cli import main

def test_version_flag(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["geoai_cli.py", "--version"])

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "GeoAI CLI" in captured.out
