import argparse
from geoai_cli import _build_parser

def test_build_parser_returns_argument_parser():
    """Verify that _build_parser() returns an instance of argparse.ArgumentParser."""
    parser = _build_parser()
    assert isinstance(parser, argparse.ArgumentParser)

def test_build_parser_help_output():
    """Verify that the parser help output contains known subcommands like list-tools and chat."""
    parser = _build_parser()
    help_text = parser.format_help()
    assert "list-tools" in help_text
    assert "chat" in help_text
