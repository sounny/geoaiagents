import sys
from geoai_cli import _read_value_or_stdin

def test_read_value_or_stdin_locking_tty_empty_path_io_stub(mocker):
    assert _read_value_or_stdin('hello') == 'hello'

    mocker.patch.object(sys.stdin, 'isatty', return_value=True)
    assert _read_value_or_stdin('') == ''

    mocker.patch.object(sys.stdin, 'isatty', return_value=False)
    mocker.patch.object(sys.stdin, 'read', return_value='from-stdin\n')
    assert _read_value_or_stdin('') == 'from-stdin'
