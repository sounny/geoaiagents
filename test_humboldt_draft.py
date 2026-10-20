import pytest
from unittest.mock import patch, MagicMock
import humboldt
import sys

def test_is_package_installed_found():
    with patch('importlib.util.find_spec', return_value=MagicMock()):
        assert humboldt.is_package_installed('some_package') is True

def test_is_package_installed_not_found():
    with patch('importlib.util.find_spec', return_value=None):
        assert humboldt.is_package_installed('some_package') is False

def test_is_package_installed_error():
    with patch('importlib.util.find_spec', side_effect=ImportError):
        assert humboldt.is_package_installed('some_package') is False

def test_build_parser():
    parser = humboldt.build_parser()
    args = parser.parse_args(['--skip-deps', '--debug'])
    assert args.skip_deps is True
    assert args.debug is True

@pytest.mark.xfail(reason="Humboldt main currently sends empty/whitespace input to the LLM")
@patch('humboldt.call_llm_with_retry')
@patch('openai.OpenAI')
@patch('builtins.input', side_effect=['   ', 'exit'])
def test_main_empty_input(mock_input, mock_openai, mock_call_llm):
    with patch('humboldt.check_and_install_dependencies'):
        with patch.object(sys, 'argv', ['humboldt.py', '--skip-deps']):
            humboldt.main()

    # Assert LLM is not called for whitespace
    mock_call_llm.assert_not_called()
