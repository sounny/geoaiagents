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


def test_humboldt_untyped_params_count():
    import inspect
    import humboldt

    untyped_count = 0
    for name, obj in inspect.getmembers(humboldt, inspect.isfunction):
        if not name.startswith('_') and obj.__module__ == 'humboldt':
            sig = inspect.signature(obj)

            # Check return type
            if sig.return_annotation == inspect.Signature.empty:
                untyped_count += 1

            # Check parameters
            for param_name, param in sig.parameters.items():
                if param.annotation == inspect.Signature.empty:
                    untyped_count += 1

    assert untyped_count <= 21, f"Untyped parameters and returns count ({untyped_count}) has grown beyond the baseline (21)."
