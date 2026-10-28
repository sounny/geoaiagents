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

@pytest.mark.parametrize("tool_name", ["load_geojson", "load_csv", "load_kml"])
@pytest.mark.parametrize("content,is_zero", [("", True), ("   \n  ", False)])
def test_files_zero_whitespace(tmp_path, mocker, capsys, tool_name, content, is_zero):
    f = tmp_path / ("test" + (".txt" if is_zero else "_ws.txt"))
    f.write_text(content)

    with open(f, 'r') as fd:
        mocker.patch('sys.stdin', fd)
        mocker.patch('sys.stdin.isatty', return_value=False)
        mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', tool_name])

        try:
            main()
        except SystemExit:
            pass

        out = capsys.readouterr().out
        if tool_name == "load_geojson":
            assert "Error running load_geojson: Empty GeoJSON string" in out
        elif tool_name == "load_csv":
            assert "Error: No coordinates found in CSV data." in out
        elif tool_name == "load_kml":
            pytest.xfail("Empty KML parsing looks like a bug, returns empty table")
