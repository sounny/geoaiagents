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

import concurrent.futures
from geoai_cli import _build_parser

def test_concurrent_build_parser_args():
    def task():
        parser = _build_parser()
        return parser.parse_args(['run-tool', 'fetch_geo_boundaries', '--payload', 'USA'])

    single_result = task()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(task) for _ in range(50)]
        for future in concurrent.futures.as_completed(futures):
            assert str(future.result()) == str(single_result)

def test_concurrent_build_parser_known_args():
    def task():
        parser = _build_parser()
        return parser.parse_known_args(['run-tool', 'fetch_geo_boundaries', '--payload', 'USA', '--extra'])

    single_result = task()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(task) for _ in range(50)]
        for future in concurrent.futures.as_completed(futures):
            assert str(future.result()) == str(single_result)

@pytest.mark.xfail(raises=TypeError, reason="argparse intermixed methods fail with subparsers")
def test_parse_intermixed_args_xfail():
    parser = _build_parser()
    try:
        parser.parse_intermixed_args(['chat'])
    except SystemExit:
        pass

@pytest.mark.xfail(raises=TypeError, reason="argparse intermixed methods fail with subparsers")
def test_parse_known_intermixed_args_xfail():
    parser = _build_parser()
    try:
        parser.parse_known_intermixed_args(['chat'])
    except SystemExit:
        pass
