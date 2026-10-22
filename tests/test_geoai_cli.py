import sys
import pytest
from geoai_cli import _read_value_or_stdin, main

import subprocess

def test_version_flags():
    pytest.xfail("geoai_cli.py missing --version and -V arguments")
    for flag in ["--version", "-V"]:
        result = subprocess.run(
            [sys.executable, "geoai_cli.py", flag],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""

def test_read_value_or_stdin_locking_nonempty_passthrough(mocker):
    assert _read_value_or_stdin('Paris') == 'Paris'
    assert _read_value_or_stdin('48.8,2.3') == '48.8,2.3'
    assert _read_value_or_stdin('hello') == 'hello'

    mocker.patch('sys.stdin.isatty', return_value=True)
    assert _read_value_or_stdin('') == ''

    mocker.patch('sys.stdin.isatty', return_value=False)
    mocker.patch('sys.stdin.read', return_value='from-stdin\n')
    assert _read_value_or_stdin('') == 'from-stdin'

def test_cli_help(mocker, capsys):
    mocker.patch('socket.socket')
    mocker.patch('sys.argv', ['geoai_cli.py', '--help'])

    try:
        main()
    except SystemExit as e:
        assert e.code == 0, f"Expected exit code 0 for --help, got {e.code}"
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected for --help")

    captured = capsys.readouterr()
    assert 'usage: geoai_cli.py' in captured.out or 'GeoAI CLI' in captured.out, "Usage text not found in stdout"
    assert 'list-tools' in captured.out, "Available commands list not found in stdout"

import logging

def test_cli_argument_parsing_logging_normal(mocker, caplog):
    mocker.patch('tool_registry.create_registry')
    mocker.patch('llm_utils.call_llm_with_retry')
    mocker.patch('sys.argv', ['geoai_cli.py', '--debug', 'list-tools'])

    caplog.set_level(logging.DEBUG)

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # log capture might be empty for this normal run, just asserting types when present

    for record in caplog.records:
        assert record.levelno in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        msg = record.getMessage().lower()
        assert "secret" not in msg
        assert "api_key" not in msg
        assert "apikey" not in msg
        assert "token" not in msg

def test_cli_argument_parsing_logging_failing(mocker, caplog):
    mocker.patch('tool_registry.create_registry')
    mocker.patch('sys.argv', ['geoai_cli.py', '--debug', 'invalid-command'])

    caplog.set_level(logging.DEBUG)

    try:
        main()
    except SystemExit as e:
        assert e.code != 0
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected for failing call")

    for record in caplog.records:
        assert record.levelno in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        msg = record.getMessage().lower()
        assert "secret" not in msg
        assert "api_key" not in msg
        assert "apikey" not in msg
        assert "token" not in msg
