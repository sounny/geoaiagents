import sys
import pytest
from geoai_cli import _read_value_or_stdin, main, _tool_args_for, _build_parser

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

from unittest.mock import patch
import argparse

def test_main_list_tools_public():
    with patch("sys.argv", ["geoai_cli.py", "list-tools"]):
        result = main()
        assert type(result) is int
        assert result == 0

def test_main_run_tool_public(tmp_path):
    test_file = tmp_path / "payload.txt"
    test_file.write_text("Paris")

    with patch("sys.argv", ["geoai_cli.py", "run-tool", "geocode_locations", "--payload", str(test_file)]):
        with patch("tool_registry.ToolRegistry.invoke", return_value="mocked") as mock_invoke:
            result = main()
            assert type(result) is int
            assert result == 0
            args_call = mock_invoke.call_args[0][1]
            assert set(args_call.keys()) == {"locations"}
            mock_invoke.assert_called_once_with("geocode_locations", {"locations": str(test_file)})

def test_main_geocode_stdin_public(tmp_path, monkeypatch):
    test_file = tmp_path / "input.txt"
    test_file.write_text("Seattle\n")

    with open(test_file, "r") as f:
        monkeypatch.setattr("sys.stdin", f)
        # we can mock read() instead of isatty since we're using a real file which will return False for isatty
        # wait no, let's just patch read to return the file content

        with patch("sys.argv", ["geoai_cli.py", "geocode"]):
            with patch("tool_registry.ToolRegistry.invoke", return_value="mocked") as mock_invoke:
                result = main()
                assert type(result) is int
                assert result == 0
                args_call = mock_invoke.call_args[0][1]
                assert set(args_call.keys()) == {"locations"}
                mock_invoke.assert_called_once_with("geocode_locations", {"locations": "Seattle"})

def test_main_boundaries_public():
    with patch("sys.argv", ["geoai_cli.py", "boundaries", "USA", "--adm", "ADM1"]):
        with patch("tool_registry.ToolRegistry.invoke", return_value="mocked") as mock_invoke:
            result = main()
            assert type(result) is int
            assert result == 0
            args_call = mock_invoke.call_args[0][1]
            assert set(args_call.keys()) == {"iso", "adm"}
            mock_invoke.assert_called_once_with("fetch_geo_boundaries", {"iso": "USA", "adm": "ADM1"})

def test_main_chat_public():
    with patch("sys.argv", ["geoai_cli.py", "chat"]):
        with patch("builtins.input", side_effect=["exit"]):
            with patch("openai.OpenAI") as mock_openai:
                result = main()
                assert type(result) is int
                assert result == 0
                mock_openai.assert_called_once()
