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

from geoai_cli import _build_parser

@pytest.mark.parametrize('parse_method_name', [
    'parse_args',
    'parse_known_args',
    'parse_intermixed_args',
    'parse_known_intermixed_args'
])
def test_geoai_cli_parse_args_omitted_vs_none(mocker, parse_method_name):
    mocker.patch('sys.argv', ['geoai_cli.py', 'geocode', 'Paris'])
    parser = _build_parser()
    parse_method = getattr(parser, parse_method_name)

    try:
        res_omitted = parse_method()
    except Exception as e:
        res_omitted = e

    try:
        res_none = parse_method(None)
    except Exception as e:
        res_none = e

    if isinstance(res_omitted, Exception):
        assert isinstance(res_omitted, TypeError)
        assert "parse_intermixed_args: positional arg with nargs=A" in str(res_omitted)
        assert type(res_omitted) is type(res_none)
        assert str(res_omitted) == str(res_none)
        pytest.xfail(f"argparse bug with subparsers: {res_omitted}")

    assert res_omitted == res_none
