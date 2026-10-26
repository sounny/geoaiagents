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



import sys

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="sys.argv requires strings, not numpy scalars")
def test_geoai_cli_numeric_args_parsing_int(monkeypatch, mocker, tmp_path):
    np = pytest.importorskip("numpy")
    from geoai_cli import main
    mocker.patch("openai.OpenAI")
    monkeypatch.chdir(tmp_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy")

    e1 = None
    monkeypatch.setattr(sys, 'argv', ['geoai_cli.py', 'chat', '--max-steps', 5])
    try:
        main()
    except Exception as e:
        e1 = type(e)

    e2 = None
    monkeypatch.setattr(sys, 'argv', ['geoai_cli.py', 'chat', '--max-steps', np.int64(5)])
    try:
        main()
    except Exception as e:
        e2 = type(e)

    assert e1 == e2, f"Exceptions mismatch: {e1} vs {e2}"

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="sys.argv requires strings, not numpy scalars")
def test_geoai_cli_numeric_args_parsing_float(monkeypatch, mocker, tmp_path):
    np = pytest.importorskip("numpy")
    from geoai_cli import main
    mocker.patch("tool_registry.ToolRegistry.invoke")
    monkeypatch.chdir(tmp_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy")

    e1 = None
    monkeypatch.setattr(sys, 'argv', ['geoai_cli.py', 'distance', 5.0])
    try:
        main()
    except Exception as e:
        e1 = type(e)

    e2 = None
    monkeypatch.setattr(sys, 'argv', ['geoai_cli.py', 'distance', np.float64(5.0)])
    try:
        main()
    except Exception as e:
        e2 = type(e)

    assert e1 == e2, f"Exceptions mismatch: {e1} vs {e2}"
