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


@pytest.mark.parametrize("func_name", [
    "check_and_install_dependencies",
    "is_package_installed",
    "build_parser",
    "handle_direct_command",
    "execute_tool_loop",
    "chat_loop",
    "main",
])
def test_humboldt_empty_env_vars(func_name, monkeypatch, mocker):
    import argparse
    import sys
    from unittest.mock import MagicMock

    # Pre-emptively mock the modules to avoid ModuleNotFoundError when humboldt is evaluated
    monkeypatch.setitem(sys.modules, 'openai', MagicMock())
    monkeypatch.setitem(sys.modules, 'tool_registry', MagicMock())

    env_vars = [
        "OPENAI_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "HUMBOLDT_MODEL",
        "HUMBOLDT_MAX_STEPS",
        "HUMBOLDT_DEBUG",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv(var, "")

    mocker.patch('humboldt.call_llm_with_retry')
    mocker.patch('builtins.input', side_effect=['exit'])
    mocker.patch('sys.argv', ['humboldt.py'])
    mocker.patch('sys.exit')

    # If the function is not check_and_install_dependencies, mock it to prevent side-effects in other functions.
    # We DO NOT mock it when func_name == "check_and_install_dependencies" because we want to test its behavior.
    if func_name != "check_and_install_dependencies":
        mocker.patch('humboldt.check_and_install_dependencies')
    else:
        # For check_and_install_dependencies, mock the underlying external calls (subprocess.run) to prevent actual side-effects.
        mocker.patch('subprocess.run')

    import humboldt
    func = getattr(humboldt, func_name)

    # Construct args dynamically inside test to avoid MagicMock in parametrize
    kwargs = {}
    if func_name == "is_package_installed":
        kwargs = {"package_name": "openai"}
    elif func_name == "handle_direct_command":
        kwargs = {"user_input": "/geocode Paris", "tool_registry": MagicMock()}
    elif func_name == "execute_tool_loop":
        kwargs = {"client": MagicMock(), "args": MagicMock(max_steps=3, debug=False, model="test"), "messages": [], "functions": [], "run_tool_call": MagicMock()}
    elif func_name == "chat_loop":
        kwargs = {"client": MagicMock(), "args": MagicMock(max_steps=3, debug=False, model="test"), "messages": [], "tool_registry": MagicMock(), "functions": [], "run_tool_call": MagicMock()}

    try:
        res = func(**kwargs)
        if func_name == "build_parser":
            assert isinstance(res, argparse.ArgumentParser)
        elif func_name == "is_package_installed":
            assert isinstance(res, bool)
        elif func_name == "handle_direct_command":
            assert res is True
    except ValueError as e:
        if func_name in ("build_parser", "main"):
            pytest.xfail(f"Bug: unhandled ValueError for empty env vars - {e}")
        else:
            raise
