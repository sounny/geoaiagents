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

@pytest.mark.parametrize("max_steps_val, expected_output", [
    (0, "Response\n"),
    (-1, "[INFO] Reached maximum tool-call steps. Stopping.\n"),
    (999999999999999999999999999, "Response\n"),
    (float("inf"), "Response\n"),
    (float("nan"), ""),
])
def test_execute_tool_loop_numeric_edge_cases(mocker, capsys, max_steps_val, expected_output):
    import humboldt
    args = mocker.MagicMock()
    args.max_steps = max_steps_val
    args.debug = False
    args.model = "test-model"

    client = mocker.MagicMock()
    messages = []
    functions = []

    run_tool_call = mocker.MagicMock()

    mock_llm_res = mocker.MagicMock()
    mock_llm_res.choices = [mocker.MagicMock()]
    mock_llm_res.choices[0].message.function_call = None
    mock_llm_res.choices[0].message.content = "Response"

    mock_call_llm = mocker.patch("humboldt.call_llm_with_retry", return_value=mock_llm_res)

    humboldt.execute_tool_loop(client, args, messages, functions, run_tool_call)

    out, err = capsys.readouterr()
    assert out == expected_output
