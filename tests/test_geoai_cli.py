import pytest
from geoai_cli import _build_parser

def test_build_parser_list_and_run_tools_pure_argparse():
    parser = _build_parser()
    args = parser.parse_args(['list-tools'])
    assert args.command == 'list-tools'

    help_text = parser.format_help()
    assert 'list-tools' in help_text
    assert 'run-tool' in help_text
