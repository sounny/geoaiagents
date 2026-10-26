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

@pytest.mark.parametrize("func_name, seq_wrapper", [
    ("execute_tool_loop", list),
    pytest.param("execute_tool_loop", tuple, marks=pytest.mark.xfail(raises=AttributeError, reason="Humboldt crashes when sequence is a tuple")),
    ("chat_loop", list),
    pytest.param("chat_loop", tuple, marks=pytest.mark.xfail(raises=AttributeError, reason="Humboldt crashes when sequence is a tuple"))
])
def test_humboldt_sequence_types(func_name, seq_wrapper, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    args = MagicMock(debug=False, max_steps=1)
    run_tool_call = MagicMock()
    tool_registry = MagicMock()

    mock_llm = MagicMock()
    monkeypatch.setattr('humboldt.call_llm_with_retry', mock_llm)

    messages = [{"role": "system", "content": "hi"}]
    functions = [{"name": "func"}]

    if func_name == "execute_tool_loop":
        mock_resp = MagicMock()
        mock_msg = MagicMock(spec=['function_call', 'content'])
        mock_msg.content = None
        mock_msg.function_call = MagicMock(name="test_tool", arguments="{}")
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message = mock_msg
        mock_llm.return_value = mock_resp

        humboldt.execute_tool_loop(client, args, seq_wrapper(messages), seq_wrapper(functions), run_tool_call)

    elif func_name == "chat_loop":
        inputs = ['hello', 'exit']
        monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))

        humboldt.chat_loop(client, args, seq_wrapper(messages), tool_registry, seq_wrapper(functions), run_tool_call)
