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


from collections import OrderedDict
import copy

class SubStr(str): pass
class SubInt(int): pass
class SubList(list): pass
class SubDict(dict): pass
class SubODict(OrderedDict): pass

def test_is_package_installed_subclass():
    from humboldt import is_package_installed
    assert is_package_installed("json") == is_package_installed(SubStr("json"))

def test_handle_direct_command_subclass():
    from humboldt import handle_direct_command
    registry = MagicMock()
    registry.invoke.return_value = "res"
    plain_res = handle_direct_command("/geocode Paris", registry)
    sub_res = handle_direct_command(SubStr("/geocode Paris"), registry)
    assert plain_res == sub_res

def test_execute_tool_loop_subclass(mocker):
    from humboldt import execute_tool_loop
    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "Response"
    mock_resp.choices[0].message.function_call = None
    mock_call_llm.return_value = mock_resp

    client = MagicMock()

    args = MagicMock()
    args.max_steps = 2
    args.model = "my-model"
    args.debug = False
    messages = [{"role": "user", "content": "Hello"}]
    functions = [{"name": "func", "description": "desc"}]
    run_tool_call = MagicMock()

    execute_tool_loop(client, args, messages.copy(), functions, run_tool_call)
    plain_call_args = mock_call_llm.call_args

    args_sub = MagicMock()
    args_sub.max_steps = SubInt(2)
    args_sub.model = SubStr("my-model")
    args_sub.debug = False
    messages_sub = SubList([SubODict({"role": SubStr("user"), "content": SubStr("Hello")})])
    functions_sub = SubList([SubODict({"name": SubStr("func"), "description": SubStr("desc")})])

    execute_tool_loop(client, args_sub, messages_sub, functions_sub, run_tool_call)
    sub_call_args = mock_call_llm.call_args

    assert plain_call_args == sub_call_args

def test_chat_loop_subclass(mocker):
    from humboldt import chat_loop
    mock_input = mocker.patch('builtins.input', side_effect=['say hi', 'exit', 'say hi', 'exit'])
    mock_execute = mocker.patch('humboldt.execute_tool_loop')

    client = MagicMock()
    args = MagicMock()
    args.debug = False
    tool_registry = MagicMock()
    tool_registry.has_tool.return_value = False
    functions = []
    run_tool_call = MagicMock()

    messages = [{"role": "system", "content": "hi"}]
    chat_loop(client, args, messages.copy(), tool_registry, functions, run_tool_call)
    plain_call_args = mock_execute.call_args

    messages_sub = SubList([SubODict({"role": SubStr("system"), "content": SubStr("hi")})])
    chat_loop(client, args, messages_sub, tool_registry, functions, run_tool_call)
    sub_call_args = mock_execute.call_args

    assert plain_call_args == sub_call_args

def test_check_and_install_dependencies_no_args_tmp(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from humboldt import check_and_install_dependencies
    check_and_install_dependencies()
