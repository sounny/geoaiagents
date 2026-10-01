import os
from unittest.mock import patch
from humboldt import build_parser


def test_build_parser_default_args():
    # Mock environment variables to ensure defaults are taken from the fallback
    with patch.dict(os.environ, {}, clear=True):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.skip_deps is False
        assert args.debug is False
        assert args.max_steps == 3


def test_build_parser_override_args():
    with patch.dict(os.environ, {}, clear=True):
        parser = build_parser()
        args = parser.parse_args(
            ["--skip-deps", "--debug", "--max-steps", "5"]
        )
        assert args.skip_deps is True
        assert args.debug is True
        assert args.max_steps == 5
