import pytest
from unittest.mock import MagicMock
from humboldt import execute_tool_loop, chat_loop

def test_execute_tool_loop_functions_set(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test-model"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Done"

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    functions_set = set(["dummy"])
    execute_tool_loop(client, args, [{"role": "user"}], functions_set, MagicMock())

    assert mock_call_llm.call_args.kwargs['functions'] == functions_set

def test_execute_tool_loop_functions_frozenset(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test-model"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Done"

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    functions_fs = frozenset(["dummy"])
    execute_tool_loop(client, args, [{"role": "user"}], functions_fs, MagicMock())

    assert mock_call_llm.call_args.kwargs['functions'] == functions_fs

def test_execute_tool_loop_messages_set_no_function_call(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test-model"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Done"

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    messages_set = set(["dummy"])
    execute_tool_loop(client, args, messages_set, [], MagicMock())

    assert mock_call_llm.call_args.kwargs['messages'] == messages_set

@pytest.mark.xfail(reason="looks like a bug where execute_tool_loop calls append on messages")
def test_execute_tool_loop_messages_set_with_function_call(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test-model"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = MagicMock()
    mock_response.choices[0].message.function_call.name = "func1"
    mock_response.choices[0].message.function_call.arguments = "{}"

    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    messages_set = set(["dummy"])
    execute_tool_loop(client, args, messages_set, [], MagicMock())

@pytest.mark.xfail(reason="looks like a bug where execute_tool_loop calls append on messages")
def test_execute_tool_loop_messages_frozenset_with_function_call(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test-model"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = MagicMock()
    mock_response.choices[0].message.function_call.name = "func1"
    mock_response.choices[0].message.function_call.arguments = "{}"

    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    messages_fs = frozenset(["dummy"])
    execute_tool_loop(client, args, messages_fs, [], MagicMock())

@pytest.mark.xfail(reason="looks like a bug where chat_loop calls append on messages")
def test_chat_loop_messages_frozenset(mocker):
    client = MagicMock()
    args = MagicMock()
    args.debug = False

    mocker.patch('builtins.input', side_effect=["hello", "exit"])
    mocker.patch('humboldt.execute_tool_loop')

    messages_fs = frozenset()

    chat_loop(client, args, messages_fs, MagicMock(), [], MagicMock())

@pytest.mark.xfail(reason="looks like a bug where chat_loop calls append on messages")
def test_chat_loop_messages_set(mocker):
    client = MagicMock()
    args = MagicMock()
    args.debug = False

    mocker.patch('builtins.input', side_effect=["hello", "exit"])
    mocker.patch('humboldt.execute_tool_loop')

    messages_fs = set()

    chat_loop(client, args, messages_fs, MagicMock(), [], MagicMock())

def test_chat_loop_functions_set(mocker):
    client = MagicMock()
    args = MagicMock()
    args.debug = False

    mocker.patch('builtins.input', side_effect=["test", "exit"])
    mock_execute = mocker.patch('humboldt.execute_tool_loop')

    functions_set = set(["func1"])
    chat_loop(client, args, [], MagicMock(), functions_set, MagicMock())

    assert mock_execute.call_args[0][3] == functions_set

def test_chat_loop_functions_frozenset(mocker):
    client = MagicMock()
    args = MagicMock()
    args.debug = False

    mocker.patch('builtins.input', side_effect=["test", "exit"])
    mock_execute = mocker.patch('humboldt.execute_tool_loop')

    functions_fs = frozenset(["func1"])
    chat_loop(client, args, [], MagicMock(), functions_fs, MagicMock())

    assert mock_execute.call_args[0][3] == functions_fs
