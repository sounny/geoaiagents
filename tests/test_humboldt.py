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

import inspect

def test_humboldt_exports(mocker):
    # Mock external calls that might happen during import, though none are expected at module level,
    # it's good practice. We mock os and sys just in case, but actually importing the module is safe here.
    import humboldt

    public_names = sorted([name for name in dir(humboldt) if not name.startswith('_')])

    expected_names = [
        'argparse', 'build_parser', 'call_llm_with_retry', 'chat_loop',
        'check_and_install_dependencies', 'execute_tool_loop', 'handle_direct_command',
        'importlib', 'is_package_installed', 'logging', 'main', 'os', 'subprocess', 'sys'
    ]

    assert public_names == expected_names

    expected_types = {
        'argparse': 'constant/other',
        'build_parser': 'function',
        'call_llm_with_retry': 'function',
        'chat_loop': 'function',
        'check_and_install_dependencies': 'function',
        'execute_tool_loop': 'function',
        'handle_direct_command': 'function',
        'importlib': 'constant/other',
        'is_package_installed': 'function',
        'logging': 'constant/other',
        'main': 'function',
        'os': 'constant/other',
        'subprocess': 'constant/other',
        'sys': 'constant/other'
    }

    for name in public_names:
        obj = getattr(humboldt, name)
        if inspect.isclass(obj):
            obj_type = 'class'
        elif inspect.isfunction(obj):
            obj_type = 'function'
        else:
            obj_type = 'constant/other'

        assert obj_type == expected_types[name]
