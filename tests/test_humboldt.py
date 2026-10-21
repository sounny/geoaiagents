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

import random
import inspect
from types import FunctionType
import subprocess
import humboldt

@pytest.mark.xfail(reason="Fuzz testing exposes unexpected crashes on invalid inputs")
def test_humboldt_fuzz(mocker):
    # Mock builtins.input so functions that wait for input like chat_loop don't hang
    mocker.patch('builtins.input', side_effect=['exit'] * 1000)
    # Also mock call_llm_with_retry and OpenAI
    mocker.patch('humboldt.call_llm_with_retry')
    mocker.patch('openai.OpenAI')

    random.seed(42)

    # Generate random inputs
    base_values = [
        None, "", "   ", "a" * 10000, "ñöéü", "\x00",
        0, 1, -1, float('inf'), float('-inf'), float('nan'),
        [], {}, set(), (), True, False
    ]
    inputs = []
    for _ in range(300):
        inputs.append(random.choice(base_values))

    # Get public functions from humboldt
    public_funcs = [
        getattr(humboldt, f) for f in dir(humboldt)
        if not f.startswith('_')
        and isinstance(getattr(humboldt, f), FunctionType)
        and getattr(humboldt, f).__module__ == 'humboldt'
    ]

    # Expected exceptions from the module
    expected_exceptions = (
        ImportError,
        ValueError,
        ModuleNotFoundError,
        subprocess.CalledProcessError,
        SystemExit
    )

    import typing
    for func in public_funcs:
        sig = inspect.signature(func)
        num_args = len(sig.parameters)
        if num_args == 0:
            continue

        hints = typing.get_type_hints(func)
        return_type = hints.get('return', typing.Any)

        for _ in range(200):
            args = [random.choice(inputs) for _ in range(num_args)]
            try:
                ret = func(*args)
                # Verify return type if it's explicitly documented and not Any
                if return_type is not typing.Any:
                    # Get origin for generics
                    origin = getattr(typing, 'get_origin', lambda x: x)(return_type) or return_type
                    if isinstance(origin, type) and not isinstance(ret, origin):
                        pytest.fail(f"Invalid return type from {func.__name__}: expected {return_type}, got {type(ret)}")
            except expected_exceptions:
                pass
            except Exception as e:
                pytest.fail(f"Unexpected crash in {func.__name__} with args {args}: {type(e).__name__} - {e}")
