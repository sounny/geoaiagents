import pytest
from geoai_cli import _build_parser

def test_build_parser_commands_distinct_from_others():
    parser = _build_parser()

    args = parser.parse_args(['list-tools'])
    assert args.command == 'list-tools'

    args = parser.parse_args(['geocode', 'Paris'])
    assert args.command == 'geocode'
    assert args.value == 'Paris'

    args = parser.parse_args(['reverse'])
    assert args.command == 'reverse'

    args = parser.parse_args(['dms'])
    assert args.command == 'dms'

    args = parser.parse_args(['distance'])
    assert args.command == 'distance'
