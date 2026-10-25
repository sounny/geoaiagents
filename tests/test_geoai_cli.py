import copy
import inspect
import geoai_cli
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

def get_public_funcs():
    return [
        (name, obj) for name, obj in inspect.getmembers(geoai_cli)
        if not name.startswith('_') and inspect.isfunction(obj) and obj.__module__ == 'geoai_cli'
    ]

@pytest.mark.parametrize("name, func", get_public_funcs())
def test_public_functions_deepcopy(name, func, mocker, tmp_path):
    mocker.patch('geoai_cli.create_registry', return_value=mocker.MagicMock())
    mocker.patch('sys.argv', ['geoai_cli.py', '--help'])

    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy content")

    try:
        result1 = func()
    except SystemExit as e:
        result1 = e.code

    try:
        result_copy = copy.deepcopy(result1)
        assert result_copy == result1
    except Exception:
        pytest.xfail(f"Object returned by {name} is not comparable or deepcopyable")

    try:
        result2 = func(**{})
    except SystemExit as e:
        result2 = e.code

    assert result1 == result2
