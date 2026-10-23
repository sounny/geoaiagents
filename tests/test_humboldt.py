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


def test_check_and_install_dependencies_positional_and_keyword(mocker, capsys):
    import humboldt
    mocker.patch('os.path.exists', return_value=False)
    # No optional/required parameters for check_and_install_dependencies
    humboldt.check_and_install_dependencies()
    out, _ = capsys.readouterr()
    assert "Checking dependencies..." in out


def test_is_package_installed_positional_and_keyword(mocker):
    import humboldt
    mocker.patch('importlib.util.find_spec', return_value=True)
    # Positional
    assert humboldt.is_package_installed('openai') is True
    # Keyword
    assert humboldt.is_package_installed(package_name='openai') is True


def test_build_parser_positional_and_keyword():
    import humboldt
    # No parameters for build_parser
    parser = humboldt.build_parser()
    assert parser is not None
    assert parser.description == "Interactive GeoAI agent"


def test_handle_direct_command_positional_and_keyword(mocker, capsys):
    import humboldt
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "mock_output"

    # Positional
    result_pos = humboldt.handle_direct_command('/geocode Paris', mock_registry)
    assert result_pos is True

    # Keyword
    result_kw = humboldt.handle_direct_command(user_input='/geocode Paris', tool_registry=mock_registry)
    assert result_kw is True


def test_execute_tool_loop_positional_and_keyword(mocker):
    import humboldt
    client = mocker.MagicMock()
    args = mocker.MagicMock()
    args.max_steps = 0
    args.model = "test"
    args.debug = False
    messages = []
    functions = []
    run_tool_call = mocker.MagicMock()

    mock_call = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "hello"
    mock_call.return_value = mock_response

    # Positional
    result_pos = humboldt.execute_tool_loop(client, args, messages, functions, run_tool_call)
    assert result_pos is None

    # Keyword
    result_kw = humboldt.execute_tool_loop(
        client=client,
        args=args,
        messages=messages,
        functions=functions,
        run_tool_call=run_tool_call
    )
    assert result_kw is None


def test_chat_loop_positional_and_keyword(mocker):
    import humboldt
    client = mocker.MagicMock()
    args = mocker.MagicMock()
    messages = []
    tool_registry = mocker.MagicMock()
    functions = []
    run_tool_call = mocker.MagicMock()

    mocker.patch('builtins.input', side_effect=['exit', 'exit'])

    # Positional
    result_pos = humboldt.chat_loop(client, args, messages, tool_registry, functions, run_tool_call)
    assert result_pos is None

    # Keyword
    result_kw = humboldt.chat_loop(
        client=client,
        args=args,
        messages=messages,
        tool_registry=tool_registry,
        functions=functions,
        run_tool_call=run_tool_call
    )
    assert result_kw is None


def test_main_positional_and_keyword(mocker):
    import humboldt
    mocker.patch('sys.argv', ['humboldt.py', '--skip-deps'])
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')
    mocker.patch('tool_registry.create_registry')
    mocker.patch('humboldt.chat_loop')

    # main takes no parameters
    result = humboldt.main()
    assert result is None
