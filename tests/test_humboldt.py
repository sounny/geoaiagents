import pytest
import sys
from unittest.mock import patch, MagicMock
from humboldt import main

@pytest.mark.xfail(reason="Humboldt calls LLM for empty or whitespace-only input instead of a no-op")
def test_humboldt_empty_input(mocker, capsys):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_input = mocker.patch('builtins.input', side_effect=['', '   ', 'exit'])

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')

    # We also need to mock sys.argv
    mocker.patch('sys.argv', ['humboldt.py'])

    main()

    # Check what happens
    # It should NOT call the LLM for empty/whitespace input
    # Currently it does, so we expect this to fail.

    # Assert LLM was not called
    assert mock_call_llm.call_count == 0, "LLM was called for empty or whitespace-only input"

    out, err = capsys.readouterr()
    # It should print some informative message or no-op. If it calls the LLM, mock_call_llm.call_count is non-zero.

def test_humboldt_reload_state(mocker):
    mocker.patch('humboldt.check_and_install_dependencies')
    import importlib
    import inspect
    import humboldt
    importlib.reload(humboldt)
    public_names = sorted([name for name in dir(humboldt) if not name.startswith('_')])
    expected_names = [
        'argparse', 'build_parser', 'call_llm_with_retry', 'chat_loop',
        'check_and_install_dependencies', 'execute_tool_loop', 'handle_direct_command',
        'importlib', 'is_package_installed', 'logging', 'main', 'os', 'subprocess', 'sys'
    ]
    assert public_names == expected_names
    assert inspect.ismodule(humboldt.argparse)
    assert inspect.isfunction(humboldt.build_parser)
    assert inspect.isfunction(humboldt.call_llm_with_retry)
    assert inspect.isfunction(humboldt.chat_loop)
    assert inspect.isfunction(humboldt.check_and_install_dependencies)
    assert inspect.isfunction(humboldt.execute_tool_loop)
    assert inspect.isfunction(humboldt.handle_direct_command)
    assert inspect.ismodule(humboldt.importlib)
    assert inspect.isfunction(humboldt.is_package_installed)
    assert inspect.ismodule(humboldt.logging)
    assert inspect.isfunction(humboldt.main)
    assert inspect.ismodule(humboldt.os)
    assert inspect.ismodule(humboldt.subprocess)
    assert inspect.ismodule(humboldt.sys)
