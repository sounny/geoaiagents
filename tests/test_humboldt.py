import humboldt
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





@pytest.mark.parametrize("func_name, args", [
    ('check_and_install_dependencies', ()),
    ('is_package_installed', ("openai",)),
    ('build_parser', ()),
    ('handle_direct_command', ("/geocode Paris", MagicMock())),
    ('execute_tool_loop', (MagicMock(), MagicMock(), [], [], MagicMock())),
    ('chat_loop', (MagicMock(), MagicMock(), [], MagicMock(), [], MagicMock())),
    ('main', ()),
])
def test_public_functions_unknown_kwargs(func_name, args, mocker):
    mocker.patch('sys.argv', ['humboldt.py'])

    if func_name == 'main':
        mocker.patch('humboldt.check_and_install_dependencies')

    func = getattr(humboldt, func_name)

    # We expect strict kwarg checking, meaning unknown kwargs should raise a TypeError.
    # If a function did NOT raise TypeError (e.g., silently ignored the kwarg),
    # that would be the bug, but currently they all correctly raise TypeError.
    with pytest.raises(TypeError):
        func(*args, misspelled_kwarg=123)
