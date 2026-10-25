import pytest
import inspect
import humboldt
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

def test_build_parser_idempotency():
    # build_parser has no external dependencies or side effects
    from humboldt import build_parser
    parser1 = build_parser()
    parser2 = build_parser()

    # Mutate parser1 (it's an ArgumentParser object, no straightforward lists/dicts returned, but we can change an attribute)
    parser1.description = "Mutated"

    # Assert parser2 is untouched
    assert parser2.description == "Interactive GeoAI agent"

def test_check_and_install_dependencies_idempotency(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from humboldt import check_and_install_dependencies

    # Mock OS and subprocess to avoid actual side effects
    mocker.patch('humboldt.os.path.exists', return_value=True)
    mocker.patch('humboldt.subprocess.run')
    mocker.patch('humboldt.is_package_installed', return_value=True)

    (tmp_path / 'requirements.txt').touch()
    res1 = check_and_install_dependencies()
    res2 = check_and_install_dependencies()

    # No return value, but we assert it doesn't crash and returns None consistently
    assert res1 is None
    assert res2 is None

def test_is_package_installed_idempotency(mocker):
    from humboldt import is_package_installed
    mocker.patch('importlib.util.find_spec', return_value=True)

    res1 = is_package_installed('openai')
    res2 = is_package_installed('openai')

    assert res1 is True
    assert res2 is True

def test_handle_direct_command_idempotency():
    from humboldt import handle_direct_command
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "Success"

    res1 = handle_direct_command('/geocode New York', tool_registry)
    res2 = handle_direct_command('/geocode New York', tool_registry)

    assert res1 is True
    assert res2 is True
    assert tool_registry.invoke.call_count == 2

def test_execute_tool_loop_idempotency(mocker):
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = MagicMock(max_steps=1, debug=False, model='test')
    messages = []
    functions = []
    run_tool_call = MagicMock()

    # Mock LLM response to exit loop immediately
    mock_choice = MagicMock()
    mock_choice.message.function_call = None
    mock_choice.message.content = "Done"
    mocker.patch('humboldt.call_llm_with_retry', return_value=MagicMock(choices=[mock_choice]))

    res1 = execute_tool_loop(client, args, messages, functions, run_tool_call)
    # messages is mutated in execute_tool_loop if function call, but here content is printed and breaks.

    # Mutate to see if it breaks anything
    messages.append("Mutated")

    # Call 2
    res2 = execute_tool_loop(client, args, messages, functions, run_tool_call)

    assert res1 is None
    assert res2 is None

def test_chat_loop_idempotency(mocker):
    from humboldt import chat_loop
    client = MagicMock()
    args = MagicMock(max_steps=1, debug=False, model='test')
    messages = []
    tool_registry = MagicMock()
    functions = []
    run_tool_call = MagicMock()

    # Provide enough 'exit' to exit loop on both calls
    mocker.patch('builtins.input', side_effect=['exit', 'exit'])

    res1 = chat_loop(client, args, messages, tool_registry, functions, run_tool_call)
    messages.append("Mutated")
    res2 = chat_loop(client, args, messages, tool_registry, functions, run_tool_call)

    assert res1 is None
    assert res2 is None

def test_main_idempotency(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from humboldt import main

    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('sys.argv', ['humboldt.py', '--skip-deps'])
    mocker.patch('builtins.input', side_effect=['exit', 'exit'])

    # Mock modules
    mocker.patch.dict('sys.modules', {
        'openai': MagicMock(),
        'tool_registry': MagicMock()
    })

    res1 = main()
    res2 = main()

    assert res1 is None
    assert res2 is None
