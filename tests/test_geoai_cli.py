import sys
import pytest
from geoai_cli import _read_value_or_stdin, _tool_args_for

def test_tool_args_for_fetch_geo_boundaries_adm0():
    assert _tool_args_for('fetch_geo_boundaries', 'USA', 'ADM0') == {'iso': 'USA', 'adm': 'ADM0'}
    assert _tool_args_for('fetch_geo_boundaries', 'usa', 'ADM0') == {'iso': 'usa', 'adm': 'ADM0'}

def test_read_value_or_stdin_locking_nonempty_passthrough(mocker):
    assert _read_value_or_stdin('Paris') == 'Paris'
    assert _read_value_or_stdin('48.8,2.3') == '48.8,2.3'
    assert _read_value_or_stdin('hello') == 'hello'

    mocker.patch('sys.stdin.isatty', return_value=True)
    assert _read_value_or_stdin('') == ''

    mocker.patch('sys.stdin.isatty', return_value=False)
    mocker.patch('sys.stdin.read', return_value='from-stdin\n')
    assert _read_value_or_stdin('') == 'from-stdin'
