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

import humboldt

@pytest.mark.xfail(reason="Some callables are missing docstrings")
def test_humboldt_callables_have_docstrings():
    module = humboldt
    if hasattr(module, '__all__'):
        names = module.__all__
    else:
        names = [n for n in dir(module) if not n.startswith('_')]

    allowlist = []

    missing = []
    for name in names:
        obj = getattr(module, name)
        if callable(obj):
            if not obj.__doc__ and name not in allowlist:
                missing.append(name)

    if missing:
        pytest.fail(f"Missing docstrings for: {', '.join(missing)}")
