import sys
from unittest.mock import patch
from geoai_cli import _read_value_or_stdin

def test_read_value_or_stdin_value():
    assert _read_value_or_stdin('hello') == 'hello'

def test_read_value_or_stdin_empty_isatty():
    with patch('sys.stdin.isatty', return_value=True):
        assert _read_value_or_stdin('') == ''
