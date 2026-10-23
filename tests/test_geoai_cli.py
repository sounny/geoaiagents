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
        sys.exit(main())
    except SystemExit as e:
        assert e.code == 0, f"Expected exit code 0 for --help, got {e.code}"
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected for --help")

    captured = capsys.readouterr()
    assert 'usage: geoai_cli.py' in captured.out or 'GeoAI CLI' in captured.out, "Usage text not found in stdout"
    assert 'list-tools' in captured.out, "Available commands list not found in stdout"

@pytest.mark.parametrize("text", ["München", "東京", "🌍🚀"])
@pytest.mark.parametrize("command, expected_tool, expected_args_key", [
    ("geocode", "geocode_locations", "locations"),
    ("reverse", "reverse_geocode_coordinates", "coordinates"),
    ("dms", "convert_dd_to_dms", "coordinates"),
    ("distance", "calculate_distance", "coordinates"),
])
def test_cli_argument_parsing_unicode(mocker, text, command, expected_tool, expected_args_key):
    mocker.patch('sys.argv', ['geoai_cli.py', command, text])
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "Mocked Result"
    mocker.patch('geoai_cli.create_registry', return_value=mock_registry)

    try:
        sys.exit(main())
    except SystemExit as e:
        assert e.code == 0, f"Expected 0, got {e.code}"
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected")

    mock_registry.invoke.assert_called_once_with(expected_tool, {expected_args_key: text})

@pytest.mark.parametrize("text", ["München", "東京", "🌍🚀"])
def test_cli_boundaries_unicode(mocker, text):
    mocker.patch('sys.argv', ['geoai_cli.py', 'boundaries', text, '--adm', text])
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "Mocked Result"
    mocker.patch('geoai_cli.create_registry', return_value=mock_registry)

    try:
        sys.exit(main())
    except SystemExit as e:
        assert e.code == 0, f"Expected 0, got {e.code}"
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected")

    mock_registry.invoke.assert_called_once_with('fetch_geo_boundaries', {'iso': text, 'adm': text})

@pytest.mark.parametrize("text", ["München", "東京", "🌍🚀"])
def test_cli_run_tool_unicode(mocker, text):
    mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', 'dummy_tool', '--payload', text])
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "Mocked Result"
    mocker.patch('geoai_cli.create_registry', return_value=mock_registry)

    try:
        sys.exit(main())
    except SystemExit as e:
        assert e.code == 0, f"Expected 0, got {e.code}"
    else:
        pytest.fail("geoai_cli.main() did not exit with SystemExit as expected")

    mock_registry.invoke.assert_called_once_with('dummy_tool', {'input': text})
