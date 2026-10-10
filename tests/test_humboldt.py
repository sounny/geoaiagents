import argparse
from humboldt import is_package_installed, build_parser

def test_is_package_installed_nonsense():
    assert is_package_installed("some_nonsense_package_123456789") is False
    # Also sanity check something we know is installed (if any) or just the negative case.

def test_build_parser_flags():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)

    # Check for expected top-level flags
    actions = {action.dest for action in parser._actions}
    expected_flags = {'base_url', 'api_key', 'model', 'skip_deps', 'max_steps', 'debug', 'help'}

    for flag in expected_flags:
        assert flag in actions, f"Expected flag {flag} not found in parser"
