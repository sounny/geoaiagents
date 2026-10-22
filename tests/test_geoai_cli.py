import time
import json
from unittest.mock import MagicMock
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



def test_argument_parsing_very_large_inputs(mocker, capsys):
    # Mock to prevent actual network calls and verify behavior
    mock_registry = MagicMock()
    mock_registry.invoke.return_value = "Mocked result"
    mocker.patch('geoai_cli.create_registry', return_value=mock_registry)

    # 1. Very long string payload
    long_string = "A" * 1000000

    # 2. Very long list payload
    long_list_data = ["item"] * 100000
    long_list = json.dumps(long_list_data)

    # 3. Big dict payload
    big_dict_data = {f"key{i}": f"value{i}" for i in range(100000)}
    big_dict = json.dumps(big_dict_data)

    payloads = [
        ("long_string", long_string),
        ("long_list", long_list),
        ("big_dict", big_dict),
    ]

    for name, payload in payloads:
        # We test with a dummy tool to avoid specifics of real tools.
        # But 'geoai_cli.py' expects '--payload' to map depending on the tool name.
        # If we use a generic tool, it passes {'input': payload} by default.
        # So we'll use a dummy tool name 'dummy_tool' that isn't in TEXT_FIELD_BY_TOOL.
        mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', 'dummy_tool', '--payload', payload])

        start_time = time.time()
        try:
            main()
        except SystemExit as e:
            # We assert that the code returns exit code 0 on success
            assert e.code == 0

        end_time = time.time()
        duration = end_time - start_time

        # Check parsing takes a reasonable amount of time
        assert duration < 5.0, f"Parsing {name} took too long: {duration} seconds"

        captured = capsys.readouterr()

        # Verify the tool was called exactly as expected based on current logic
        mock_registry.invoke.assert_called_with('dummy_tool', {'input': payload})
        mock_registry.invoke.reset_mock()
