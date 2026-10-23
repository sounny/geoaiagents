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

def test_humboldt_public_callables_accept_types(mocker):
    # check_and_install_dependencies takes no arguments
    mocker.patch('humboldt.subprocess.run')
    mocker.patch('humboldt.os.path.exists', return_value=False)

    import humboldt
    humboldt.check_and_install_dependencies()

    # is_package_installed takes a str
    assert isinstance(humboldt.is_package_installed('openai'), bool)

    # build_parser takes no arguments
    parser = humboldt.build_parser()

    # handle_direct_command takes a str and a tool_registry
    mock_registry = MagicMock()
    humboldt.handle_direct_command("/geocode Paris", mock_registry)

    # execute_tool_loop takes client, args, messages, functions, run_tool_call
    mock_client = MagicMock()
    mock_args = MagicMock(max_steps=0, debug=False, model="test")
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message.function_call = None
    mock_llm_response.choices[0].message.content = "test"
    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_llm_response)
    humboldt.execute_tool_loop(mock_client, mock_args, [], [], MagicMock())

    # chat_loop takes client, args, messages, tool_registry, functions, run_tool_call
    mocker.patch('builtins.input', return_value='exit')
    humboldt.chat_loop(mock_client, mock_args, [], mock_registry, [], MagicMock())

    # main takes no arguments
    mocker.patch('sys.argv', ['humboldt.py'])
    mocker.patch('humboldt.chat_loop')
    humboldt.main()
