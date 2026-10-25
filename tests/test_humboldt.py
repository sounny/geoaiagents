import os
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

def test_build_parser_pos_vs_kw():
    res_pos = humboldt.build_parser()
    res_kw = humboldt.build_parser(**{})
    assert type(res_pos) == type(res_kw)
    assert res_pos.description == res_kw.description

def test_check_and_install_dependencies_pos_vs_kw(mocker, tmp_path):
    mocker.patch('subprocess.run')
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        res_pos = humboldt.check_and_install_dependencies()
        res_kw = humboldt.check_and_install_dependencies(**{})
        assert res_pos == res_kw == None
    finally:
        os.chdir(cwd)

def test_is_package_installed_pos_vs_kw(mocker):
    mocker.patch('importlib.util.find_spec', return_value=MagicMock())
    res_pos = humboldt.is_package_installed('openai')
    res_kw = humboldt.is_package_installed(package_name='openai')
    assert res_pos == res_kw == True

def test_handle_direct_command_pos_vs_kw():
    mock_registry = MagicMock()
    mock_registry.invoke.return_value = "Result"
    res_pos = humboldt.handle_direct_command("/geocode Paris", mock_registry)
    res_kw = humboldt.handle_direct_command(user_input="/geocode Paris", tool_registry=mock_registry)
    assert res_pos == res_kw == True

def test_execute_tool_loop_pos_vs_kw(mocker):
    mocker.patch('humboldt.call_llm_with_retry', return_value=MagicMock(choices=[MagicMock(message=MagicMock(function_call=None, content="done"))]))
    client = MagicMock()
    args = MagicMock(max_steps=0, model='test', debug=False)
    messages_pos = []
    messages_kw = []
    functions = []
    run_tool_call = MagicMock()

    humboldt.execute_tool_loop(client, args, messages_pos, functions, run_tool_call)
    humboldt.execute_tool_loop(client=client, args=args, messages=messages_kw, functions=functions, run_tool_call=run_tool_call)

    assert messages_pos == messages_kw

def test_chat_loop_pos_vs_kw(mocker):
    mocker.patch('builtins.input', side_effect=['exit', 'exit'])
    client = MagicMock()
    args = MagicMock()
    messages_pos = []
    messages_kw = []
    tool_registry = MagicMock()
    functions = []
    run_tool_call = MagicMock()

    humboldt.chat_loop(client, args, messages_pos, tool_registry, functions, run_tool_call)
    humboldt.chat_loop(client=client, args=args, messages=messages_kw, tool_registry=tool_registry, functions=functions, run_tool_call=run_tool_call)

    assert messages_pos == messages_kw

def test_main_pos_vs_kw(mocker):
    mock_parser = MagicMock()
    mock_parser.parse_known_args.return_value = (MagicMock(skip_deps=True, debug=False, model='test'), [])
    mocker.patch('humboldt.build_parser', return_value=mock_parser)
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('sys.argv', ['humboldt.py', '--skip-deps'])
    mocker.patch('humboldt.chat_loop')

    mocker.patch('tool_registry.create_registry')
    mocker.patch('openai.OpenAI')

    res_pos = humboldt.main()
    res_kw = humboldt.main(**{})
    assert res_pos == res_kw == None

def test_call_llm_with_retry_pos_vs_kw(mocker):
    # It is imported into humboldt, testing it just in case
    mocker.patch('time.sleep')
    client = MagicMock()
    mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content="hi"))])
    client.chat.completions.create.return_value = mock_response

    res_pos = humboldt.call_llm_with_retry(client, 1)
    res_kw = humboldt.call_llm_with_retry(client=client, max_retries=1)

    assert res_pos == res_kw
