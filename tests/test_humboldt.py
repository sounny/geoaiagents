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

def test_is_package_installed_edge_cases():
    from humboldt import is_package_installed

    # Empty string returns False (or similar non-exception fallback)
    assert not is_package_installed("")

    # None raises AttributeError
    with pytest.raises(AttributeError):
        is_package_installed(None)

    # int raises AttributeError
    with pytest.raises(AttributeError):
        is_package_installed(123)

    # List raises TypeError
    with pytest.raises(TypeError):
        is_package_installed([])

def test_handle_direct_command_edge_cases():
    from humboldt import handle_direct_command

    # Empty string user_input
    assert not handle_direct_command("", None)

    # None user_input raises AttributeError
    with pytest.raises(AttributeError):
        handle_direct_command(None, None)

    # int user_input raises AttributeError
    with pytest.raises(AttributeError):
        handle_direct_command(123, None)

    # Valid command but None tool_registry raises AttributeError
    with pytest.raises(AttributeError):
        handle_direct_command("/geocode Paris", None)

def test_execute_tool_loop_edge_cases(capsys):
    from humboldt import execute_tool_loop
    from unittest.mock import MagicMock

    client = MagicMock()

    # args=None raises AttributeError
    with pytest.raises(AttributeError):
        execute_tool_loop(client, None, [], [], None)

    # args.max_steps < 0 doesn't loop and just prints the info message
    args = MagicMock()
    args.max_steps = -1
    args.debug = False

    execute_tool_loop(client, args, [], [], None)
    out, _ = capsys.readouterr()
    assert "[INFO] Reached maximum tool-call steps. Stopping." in out
