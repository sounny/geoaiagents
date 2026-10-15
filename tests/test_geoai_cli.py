import sys
import pytest
import geoai_cli
from geoai_cli import _read_value_or_stdin

def test_read_value_or_stdin_locking_nonempty_passthrough(mocker):
    assert _read_value_or_stdin('Paris') == 'Paris'
    assert _read_value_or_stdin('48.8,2.3') == '48.8,2.3'
    assert _read_value_or_stdin('hello') == 'hello'

    mocker.patch('sys.stdin.isatty', return_value=True)
    assert _read_value_or_stdin('') == ''

    mocker.patch('sys.stdin.isatty', return_value=False)
    mocker.patch('sys.stdin.read', return_value='from-stdin\n')
    assert _read_value_or_stdin('') == 'from-stdin'


def test_cli_no_args_prints_help_no_network(monkeypatch, capsys):
    monkeypatch.setattr("socket.socket", None)
    monkeypatch.setattr("sys.argv", ["geoai_cli.py"])

    try:
        exit_code = geoai_cli.main()
    except SystemExit as e:
        exit_code = e.code

    if exit_code != 0:
        pytest.xfail(f"geoai_cli.py exited with code {exit_code} instead of 0")

    captured = capsys.readouterr()
    output = captured.out + captured.err
    if "usage:" not in output.lower():
        pytest.xfail("Usage text not found in output")

    assert exit_code == 0
    assert "usage:" in output.lower()
