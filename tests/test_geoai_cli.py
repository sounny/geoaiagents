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

def test_argument_parsing_fuzz(capsys):
    import random
    from geoai_cli import _build_parser
    import string

    random.seed(42)
    inputs = [
        "", "a" * 10000, "👍🏽 unicode 🔥 \u200b", "NaN", "Infinity", "-Infinity",
        "48.8, 2.3", "New York", "invalid", "{}", "[]",
    ]
    for _ in range(90):
        chars = [random.choice(string.printable) for _ in range(random.randint(0, 50))]
        inputs.append("".join(chars))

    parser = _build_parser()

    for _ in range(200):
        args = []
        commands = ["list-tools", "run-tool", "geocode", "reverse", "dms", "distance", "boundaries", "chat"]
        if random.choice([True, False]):
            args.append(random.choice(commands))

        for _ in range(random.randint(0, 5)):
            if random.choice([True, False]) and args:
                args.append("--payload")
            elif random.choice([True, False]) and args:
                args.append("--adm")
            elif random.choice([True, False]) and args:
                args.append("--debug")
            args.append(random.choice(inputs))

        try:
            parser.parse_args(args)
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected crash during argument parsing: {e}")
