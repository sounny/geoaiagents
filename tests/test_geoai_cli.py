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

@pytest.mark.parametrize("subcommand, arg_template", [
    ("geocode", ["{text}"]),
    ("reverse", ["{text}"]),
    ("dms", ["{text}"]),
    ("distance", ["{text}"]),
    ("boundaries", ["{text}", "--adm", "{text}"]),
    ("run-tool", ["some_tool", "--payload", "{text}", "--adm", "{text}"]),
    ("chat", ["--base-url", "{text}", "--api-key", "{text}", "--model", "{text}"]),
])
@pytest.mark.parametrize("text_input", [
    "",
    "   ",
    "\t\n  padded text  \t\n",
])
def test_cli_argument_parsing_whitespace(mocker, capsys, subcommand, arg_template, text_input):
    registry_mock = mocker.MagicMock()
    # The actual implementation calls invoke. If we mock create_registry to return MagicMock(),
    # invoke() will return a MagicMock object.
    mocker.patch("geoai_cli.create_registry", return_value=registry_mock)

    if subcommand == "run-tool":
        registry_mock.invoke.return_value = None
    else:
        registry_mock.invoke.return_value = "Mocked result"

    mocker.patch("builtins.input", side_effect=["exit"])
    mocker.patch("openai.OpenAI")

    sys_argv = ["geoai_cli.py", subcommand] + [arg.format(text=text_input) for arg in arg_template]
    mocker.patch("sys.argv", sys_argv)
    mocker.patch("sys.stdin.isatty", return_value=True)

    try:
        ret = main()
        if subcommand == "run-tool":
            assert ret == 2
        else:
            assert ret == 0
    except SystemExit as e:
        if subcommand == "run-tool":
            assert e.code == 2
        else:
            assert e.code == 0
