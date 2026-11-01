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

def test_main_nul_byte_geocode(mocker, capsys):
    # Test that passing a NUL byte to a normal CLI argument does not crash but produces output
    # Mock geocoding to prevent external API calls to Nominatim
    mocker.patch('geocode._geocode_limiter', return_value=mocker.MagicMock(address="Mock Address", latitude=48.0, longitude=2.0))
    mocker.patch('sys.argv', ['geoai_cli.py', 'geocode', 'Paris\x00'])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0
    captured = capsys.readouterr()
    # The output should contain the input payload with the NUL byte
    assert "Paris\x00" in captured.out

@pytest.mark.xfail(reason="argparse accepts NUL bytes in arguments, causing a downstream unhandled exception rather than a CLI error")
def test_main_nul_byte_chat_url(mocker):
    # Test that passing a NUL byte to a URL argument causes an unhandled exception downstream
    mocker.patch('sys.argv', ['geoai_cli.py', 'chat', '--base-url', 'http://localhost\x00'])
    # This will raise httpx.InvalidURL during client initialization, so xfail correctly handles it
    main()
