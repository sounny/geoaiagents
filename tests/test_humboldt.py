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

@pytest.mark.xfail(reason="Humboldt mutates sequence arguments instead of returning new sequences", strict=True)
def test_humboldt_execute_tool_loop_tuple(mocker):
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.debug = False

    # Needs to be a list because the tool loop appends to it. If it doesn't we get AttributeError
    messages = ({"role": "system", "content": "foo"},)
    functions = ()
    run_tool_call = MagicMock()

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = MagicMock()
    mock_message.function_call.name = "test"
    mock_message.function_call.arguments = "{}"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_call_llm.return_value = mock_response

    try:
        execute_tool_loop(client, args, messages, functions, run_tool_call)
    except AttributeError as e:
        pytest.fail(f"Raised AttributeError: {e}")

@pytest.mark.xfail(reason="Humboldt mutates sequence arguments instead of returning new sequences", strict=True)
def test_humboldt_execute_tool_loop_frozenset(mocker):
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.debug = False

    class HashableDict(dict):
        def __hash__(self):
            return 0

    messages = frozenset([HashableDict({"role": "system", "content": "foo"})])
    functions = ()
    run_tool_call = MagicMock()

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = MagicMock()
    mock_message.function_call.name = "test"
    mock_message.function_call.arguments = "{}"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_call_llm.return_value = mock_response

    try:
        execute_tool_loop(client, args, messages, functions, run_tool_call)
    except AttributeError as e:
        pytest.fail(f"Raised AttributeError: {e}")

@pytest.mark.xfail(reason="Humboldt mutates sequence arguments instead of returning new sequences", strict=True)
def test_humboldt_chat_loop_tuple(mocker):
    from humboldt import chat_loop
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.debug = False
    messages = ({"role": "system", "content": "foo"},)
    functions = ()
    run_tool_call = MagicMock()
    tool_registry = MagicMock()

    mocker.patch('humboldt.handle_direct_command', return_value=False)
    mocker.patch('builtins.input', side_effect=["hi", "exit"])

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "Hello"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_call_llm.return_value = mock_response

    try:
        chat_loop(client, args, messages, tool_registry, functions, run_tool_call)
    except AttributeError as e:
        pytest.fail(f"Raised AttributeError: {e}")

@pytest.mark.xfail(reason="Humboldt mutates sequence arguments instead of returning new sequences", strict=True)
def test_humboldt_chat_loop_frozenset(mocker):
    from humboldt import chat_loop
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.debug = False

    class HashableDict(dict):
        def __hash__(self):
            return 0

    messages = frozenset([HashableDict({"role": "system", "content": "foo"})])
    functions = ()
    run_tool_call = MagicMock()
    tool_registry = MagicMock()

    mocker.patch('humboldt.handle_direct_command', return_value=False)
    mocker.patch('builtins.input', side_effect=["hi", "exit"])

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "Hello"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_call_llm.return_value = mock_response

    try:
        chat_loop(client, args, messages, tool_registry, functions, run_tool_call)
    except AttributeError as e:
        pytest.fail(f"Raised AttributeError: {e}")
