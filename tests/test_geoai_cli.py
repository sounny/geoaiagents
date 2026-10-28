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

def test_arg_parsing_twice():
    from geoai_cli import _build_parser
    parser = _build_parser()

    # test multiple parses with same args return identical outputs
    # os.getenv calls are made at definition/build time, not parse time
    args_list = [
        ["geocode", "London"],
        ["reverse", "51.5,-0.1"],
        ["chat", "--model", "test-model"],
        ["boundaries", "GBR"]
    ]
    for args in args_list:
        args1 = parser.parse_args(args)
        args2 = parser.parse_args(args)
        assert args1 == args2

def test_main_twice(mocker):
    import io
    from contextlib import redirect_stdout, redirect_stderr
    from geoai_cli import main

    def run_main(args):
        mocker.patch('sys.argv', ['geoai_cli.py'] + args)
        f_out = io.StringIO()
        f_err = io.StringIO()
        with redirect_stdout(f_out), redirect_stderr(f_err):
            try:
                ret = main()
            except SystemExit as e:
                ret = e.code
        return ret, f_out.getvalue(), f_err.getvalue()

    commands = [
        [],
        ["--help"],
        ["list-tools"],
        ["geocode", "Paris"],
        ["reverse", "48.8,2.3"],
        ["dms", "48.8,2.3"],
        ["distance", "48.8,2.3,49.0,2.0"],
        ["boundaries", "USA"],
        ["run-tool", "geocode_locations", "--payload", "Paris"],
        ["chat", "--model", "test-model"],
    ]

    for cmd in commands:
        mock_create = mocker.patch('tool_registry.create_registry')
        mocker.patch('openai.OpenAI')
        mocker.patch('builtins.input', side_effect=['exit', 'exit'])

        mock_registry = mock_create.return_value
        mock_registry.openai_functions.return_value = [{"name": "test", "description": "test"}]
        mock_registry.invoke.return_value = "mock_result"

        ret1, out1, err1 = run_main(cmd)
        ret2, out2, err2 = run_main(cmd)

        assert ret1 == ret2
        assert out1 == out2
        assert err1 == err2
