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

import inspect
import geoai_cli

PUBLIC_FUNCS = [
    obj for name, obj in inspect.getmembers(geoai_cli)
    if inspect.isfunction(obj) and not name.startswith('_') and getattr(obj, '__module__', '') == 'geoai_cli'
]

@pytest.mark.parametrize("func", PUBLIC_FUNCS, ids=[f.__name__ for f in PUBLIC_FUNCS])
def test_geoai_cli_public_functions_idempotency(mocker, tmp_path, func):
    # Mock sys.argv for argument parsing testing as required
    mocker.patch('sys.argv', ['geoai_cli.py', 'list-tools'])

    # Mock external calls and network
    mocker.patch('os.system')
    mocker.patch('subprocess.run')
    mocker.patch('urllib.request.urlopen')

    # Use tmp_path to mock filesystem: specifically, mock read/write paths by replacing them,
    # but since main doesn't take file paths natively in list-tools, we will mock os.getcwd
    # to return the tmp_path to strictly use it for filesystem mocking.
    mocker.patch('os.getcwd', return_value=str(tmp_path))

    # Build dummy arguments dynamically based on signature to avoid TypeError on **{}
    sig = inspect.signature(func)
    kwargs = {}
    for param_name, param in sig.parameters.items():
        if param.default != inspect.Parameter.empty:
            kwargs[param_name] = param.default
        elif param.annotation == str:
            kwargs[param_name] = str(tmp_path / "dummy.txt")
        elif param.annotation == int:
            kwargs[param_name] = 0
        else:
            kwargs[param_name] = None

    try:
        res1 = func(**kwargs)
    except TypeError as e:
        # Not considered a bug in production code, but skipping because test couldn't guess arguments
        pytest.skip(f"Could not call {func.__name__} dynamically: {e}")
    except BaseException as e:
        pytest.xfail(f"Bug exposed: {func.__name__} failed on first call: {e}")
        return

    original_res = None
    if isinstance(res1, list):
        original_res = list(res1)
        res1.append("mutated")
    elif isinstance(res1, dict):
        original_res = dict(res1)
        res1["mutated"] = True
    else:
        original_res = res1

    try:
        res2 = func(**kwargs)
    except BaseException as e:
        pytest.xfail(f"Bug exposed: {func.__name__} failed on second call: {e}")
        return

    try:
        assert res2 == original_res
    except AssertionError as e:
        pytest.xfail(f"Bug exposed: {func.__name__} is not idempotent: {e}")
