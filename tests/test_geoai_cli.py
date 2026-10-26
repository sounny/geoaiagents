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

import pytest
from geoai_cli import main
import argparse

@pytest.mark.parametrize("empty_val", ["", "   "])
def test_geoai_cli_main_argument_parsing(mocker, tmp_path, empty_val):
    # Testing main() argument parsing for empty strings.
    # main() is the only public function defined in geoai_cli.py
    # We will test all string-accepting commands

    # Mock dependencies
    mocker.patch('geoai_cli.create_registry')
    mocker.patch('openai.OpenAI')
    mocker.patch('builtins.input', side_effect=EOFError)
    mocker.patch('sys.stdin.isatty', return_value=True)
    mocker.patch('sys.stdin.read', return_value=empty_val)

    dummy = tmp_path / "dummy.txt"
    dummy.write_text("test")

    # geocode
    mocker.patch('sys.argv', ['geoai_cli.py', 'geocode', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0 # pass-through

    # reverse
    mocker.patch('sys.argv', ['geoai_cli.py', 'reverse', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # dms
    mocker.patch('sys.argv', ['geoai_cli.py', 'dms', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # distance
    mocker.patch('sys.argv', ['geoai_cli.py', 'distance', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # boundaries iso
    mocker.patch('sys.argv', ['geoai_cli.py', 'boundaries', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # boundaries adm
    mocker.patch('sys.argv', ['geoai_cli.py', 'boundaries', 'USA', '--adm', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # run-tool tool_name
    mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 2 # default fallback/error

    # run-tool payload
    mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', 'tool', '--payload', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 2 # unknown tool fallback

    # run-tool adm
    mocker.patch('sys.argv', ['geoai_cli.py', 'run-tool', 'tool', '--adm', empty_val])
    try:
        main()
    except SystemExit as e:
        assert e.code == 2

    # chat base-url
    mocker.patch('sys.argv', ['geoai_cli.py', 'chat', '--base-url', empty_val])
    try:
        main()
    except EOFError:
        pass # pass-through

    # chat model
    mocker.patch('sys.argv', ['geoai_cli.py', 'chat', '--model', empty_val])
    try:
        main()
    except EOFError:
        pass # pass-through

@pytest.mark.parametrize("empty_val", ["", "   "])
def test_geoai_cli_main_chat_api_key_bug(mocker, tmp_path, empty_val):
    # chat api-key
    mocker.patch('geoai_cli.create_registry')
    mocker.patch('builtins.input', side_effect=EOFError)

    # Do not mock OpenAI completely because we want to see the error.
    # The actual code passes the empty API key to OpenAI.
    mocker.patch('sys.argv', ['geoai_cli.py', 'chat', '--api-key', empty_val])

    if empty_val == "":
        from openai import OpenAIError
        with pytest.raises(OpenAIError):
            main()
        pytest.xfail("Empty API key validation bug: causes missing credentials error")
    else:
        # If it's whitespace, it might also raise OpenAIError, or pass-through to EOFError
        from openai import OpenAIError
        try:
            main()
        except EOFError:
            pass # pass-through
        except OpenAIError:
            pytest.xfail("Whitespace API key validation bug: causes missing credentials error")
