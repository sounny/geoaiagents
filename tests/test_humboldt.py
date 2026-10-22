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

@pytest.mark.parametrize("max_steps_val, expected_exit", [
    ("0", None),
    ("1", None),
    (str(-sys.maxsize), None),
    (str(sys.maxsize), None),
    ("", SystemExit),
    ("ñ", SystemExit),
])
def test_humboldt_max_steps_boundaries(mocker, max_steps_val, expected_exit):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked response"
    mock_response.choices[0].message.function_call = None
    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    mocker.patch('builtins.input', side_effect=['exit'])
    mocker.patch('sys.argv', ['humboldt.py', '--max-steps', max_steps_val])

    if expected_exit:
        with pytest.raises(expected_exit):
            main()
    else:
        main()
