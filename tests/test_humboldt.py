import argparse
from collections import UserList

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

@pytest.mark.skip(reason="No public function in humboldt.py takes a dictionary parameter directly")
def test_humboldt_dict_subclasses():
    pass

@pytest.mark.xfail(reason="chat_loop reassigns instead of slice assignment, so passed in list subclass is not truncated in caller's scope")
def test_humboldt_list_subclasses(mocker):
    from humboldt import chat_loop
    client = MagicMock()
    args = argparse.Namespace(max_steps=0, model='test', debug=False)

    # Use UserList subclass
    messages = UserList([{"role": "system", "content": f"hi {i}"} for i in range(25)])
    functions = UserList([])

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.choices[0].message.function_call = None

    mocker.patch('llm_utils.call_llm_with_retry', return_value=mock_response)
    mocker.patch('builtins.input', side_effect=['exit'])

    chat_loop(client, args, messages, MagicMock(), functions, MagicMock())

    # The list should have been truncated to <= 20
    assert len(messages) <= 20
