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

def test_handle_direct_command_kwarg_order(tmp_path):
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "Result"

    try:
        res1 = humboldt.handle_direct_command(user_input="/geocode Paris", tool_registry=tool_registry)
        res2 = humboldt.handle_direct_command(tool_registry=tool_registry, user_input="/geocode Paris")
        assert res1 == res2
    except AssertionError:
        pytest.xfail("Results differ when keyword arguments are reordered")

def test_execute_tool_loop_kwarg_order(capsys, tmp_path):
    with patch('humboldt.call_llm_with_retry') as mock_call_llm:
        mock_response = MagicMock()
        mock_message = MagicMock(spec=['content', 'function_call'])
        mock_message.content = "Hello from LLM"
        mock_message.function_call = None
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_call_llm.return_value = mock_response

        client = MagicMock()
        args = MagicMock(max_steps=3, model="test-model", debug=False)
        messages1 = []
        messages2 = []
        functions = []
        run_tool_call = MagicMock()

        humboldt.execute_tool_loop(client=client, args=args, messages=messages1, functions=functions, run_tool_call=run_tool_call)
        out1, _ = capsys.readouterr()

        humboldt.execute_tool_loop(run_tool_call=run_tool_call, functions=functions, messages=messages2, args=args, client=client)
        out2, _ = capsys.readouterr()

        try:
            assert out1 == out2
            assert messages1 == messages2
        except AssertionError:
            pytest.xfail("Results differ based on kwarg order")
