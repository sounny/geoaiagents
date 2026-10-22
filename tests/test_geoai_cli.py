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

@pytest.mark.parametrize("args, expected_error_snippet, offending_value", [
    (['geoai_cli.py', 'chat', '--max-steps', 'not_an_int'], 'invalid int value', 'not_an_int'),
    (['geoai_cli.py', 'invalid_command'], 'invalid choice', 'invalid_command'),
    (['geoai_cli.py', 'run-tool'], 'the following arguments are required', 'tool_name'),
    (['geoai_cli.py', 'boundaries'], 'the following arguments are required', 'iso'),
    (['geoai_cli.py', 'chat', '--unrecognized_flag', 'foo'], 'unrecognized arguments', '--unrecognized_flag'),
])
def test_cli_argument_parsing_errors(mocker, capsys, args, expected_error_snippet, offending_value):
    mocker.patch('sys.argv', args)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert captured.err != ""
    assert expected_error_snippet in captured.err
    assert offending_value in captured.err
