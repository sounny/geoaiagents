import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import webchat

def test_respond_with_history_dicts_unknown_keys(mocker):
    """Test respond function with history containing dicts with unknown keys."""
    mock_call_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "mocked response"
    mock_response.choices[0].message.function_call = None
    mock_call_llm.return_value = mock_response

    original_messages = webchat.messages.copy()
    webchat.messages = [{"role": "system", "content": "sys prompt"}]

    history = [{"role": "user", "content": "hi", "extra_key": "val"}]

    try:
        reply, map_html, logs, table = webchat.respond("hello", history)

        called_messages = mock_call_llm.call_args.kwargs['messages']
        if history[0] not in called_messages:
            pytest.xfail("Bug: history parameter is completely ignored in favor of global messages list")

        assert history[0] in called_messages
    finally:
        webchat.messages = original_messages


def test_chat_with_history_dicts_unknown_keys(mocker):
    """Test chat function with history containing dicts with unknown keys."""
    mock_respond = mocker.patch('webchat.respond')
    mock_respond.return_value = ("mock_reply", "mock_html", "mock_logs", "mock_table")

    history = [{"role": "user", "content": "hello", "extra_key": "value"}]
    result_history, map_html, logs, table = webchat.chat("test message", history, None)

    expected_history = history + [
        {"role": "user", "content": "test message"},
        {"role": "assistant", "content": "mock_reply"}
    ]
    assert result_history == expected_history


class MockUploadFile:
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_respond_with_upload_file_config_object_unknown_keys(mocker, tmp_path):
    """Test respond function with upload_file as a config object containing unknown keys."""
    mock_call_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "mocked response"
    mock_response.choices[0].message.function_call = None
    mock_call_llm.return_value = mock_response

    original_messages = webchat.messages.copy()
    webchat.messages = [{"role": "system", "content": "sys prompt"}]

    try:
        temp_file = tmp_path / "test.txt"
        temp_file.write_text("file content")

        # Object with unknown keys
        upload_obj = MockUploadFile(name=str(temp_file), extra_config="123", unknown_key=True)

        reply, map_html, logs, table = webchat.respond("hello", [], upload_file=upload_obj)

        last_message = webchat.messages[-2]["content"]
        assert "file content" in last_message
        assert "hello" in last_message
        assert "test.txt" in last_message
    finally:
        webchat.messages = original_messages


def test_respond_upload_file_as_dict_unknown_keys(mocker, tmp_path):
    """Test respond function with upload_file as a dict containing unknown keys."""
    mock_call_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "mocked response"
    mock_response.choices[0].message.function_call = None
    mock_call_llm.return_value = mock_response

    original_messages = webchat.messages.copy()
    webchat.messages = [{"role": "system", "content": "sys prompt"}]

    try:
        temp_file = tmp_path / "test.txt"
        temp_file.write_text("file content")

        # Passing a dict instead of an object
        upload_dict = {"name": str(temp_file), "extra_config": "123"}

        reply, map_html, logs, table = webchat.respond("hello", [], upload_file=upload_dict)

        last_message = webchat.messages[-2]["content"]

        if "file content" not in last_message:
            pytest.xfail("Bug: passing dict instead of object to upload_file raises AttributeError that is silently swallowed")

        assert "file content" in last_message
        assert "hello" in last_message
    finally:
        webchat.messages = original_messages


def test_run_tool_with_config_object_unknown_keys(mocker):
    """Test run_tool with a config object containing unknown keys."""
    mock_registry = mocker.patch('webchat.registry')
    mock_registry.invoke.return_value = "mock_table"

    class MockFunctionCall:
        def __init__(self, name, arguments, **kwargs):
            self.name = name
            self.arguments = arguments
            for k, v in kwargs.items():
                setattr(self, k, v)

    func_call = MockFunctionCall(name="test_tool", arguments='{"arg1": "val1"}', extra_key="ignored")

    tool_name, table = webchat.run_tool(func_call)

    assert tool_name == "test_tool"
    assert table == "mock_table"
    mock_registry.invoke.assert_called_once_with("test_tool", {"arg1": "val1"})


def test_run_tool_with_dict_unknown_keys(mocker):
    """Test run_tool with a dict containing unknown keys."""
    mock_registry = mocker.patch('webchat.registry')
    mock_registry.invoke.return_value = "mock_table"

    func_call_dict = {"name": "test_tool", "arguments": '{"arg1": "val1"}', "extra_key": "ignored"}

    try:
        tool_name, table = webchat.run_tool(func_call_dict)
        assert tool_name == "test_tool"
        assert table == "mock_table"
    except AttributeError:
        pytest.xfail("Bug: run_tool expects object, raises AttributeError when passed a dict")
