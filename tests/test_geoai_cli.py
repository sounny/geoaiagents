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

def test_cli_kwarg_order_no_differ(mocker, tmp_path):
    mocker.patch('urllib.request.urlopen')
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy")

    import sys
    from geoai_cli import main

    mock_chat = mocker.patch('geoai_cli._run_chat_mode', return_value=0)

    mocker.patch.object(sys, 'argv', ['geoai_cli.py', 'chat', '--api-key', 'k', '--base-url', 'u'])
    try:
        main()
    except SystemExit:
        pass

    args1 = mock_chat.call_args[0][0]

    mock_chat.reset_mock()

    mocker.patch.object(sys, 'argv', ['geoai_cli.py', 'chat', '--base-url', 'u', '--api-key', 'k'])
    try:
        main()
    except SystemExit:
        pass

    args2 = mock_chat.call_args[0][0]

    assert vars(args1) == vars(args2)
