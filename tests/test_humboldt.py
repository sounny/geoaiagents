import os
from unittest import mock
from humboldt import build_parser

def test_build_parser_base_url_default_and_override():
    # Clear OPENAI_BASE_URL to test default behavior
    with mock.patch.dict(os.environ, clear=True):
        parser = build_parser()
        # Check default value
        args_default = parser.parse_args([])
        assert '5272' in args_default.base_url
        assert 'localhost' in args_default.base_url or 'http' in args_default.base_url

        # Check override value
        args_override = parser.parse_args(['--base-url', 'http://example.test/v1/'])
        assert args_override.base_url == 'http://example.test/v1/'
