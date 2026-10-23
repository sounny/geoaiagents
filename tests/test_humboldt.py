import argparse
import copy
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


def test_humboldt_public_functions_twice(mocker, tmp_path, monkeypatch):
    """
    Test that calling each public function twice with the same inputs
    results in identical returns and no extra side effects, documenting current behavior.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("openai==1.0\ngeopy\n")

    # 1. build_parser
    parser1 = humboldt.build_parser()
    parser2 = humboldt.build_parser()
    assert isinstance(parser1, argparse.ArgumentParser)
    assert isinstance(parser2, argparse.ArgumentParser)
    assert vars(parser1.parse_args([])) == vars(parser2.parse_args([]))

    # 2. chat_loop
    mocker.patch("builtins.input", side_effect=["hello", "exit", "hello", "exit"])
    mocker.patch("humboldt.execute_tool_loop")

    client = mocker.MagicMock()
    args = mocker.MagicMock(debug=False)
    messages = [{"role": "system", "content": "sys"}]
    tool_registry = mocker.MagicMock()
    functions = []
    run_tool_call = mocker.MagicMock()

    messages1 = copy.deepcopy(messages)
    res1 = humboldt.chat_loop(client, args, messages1, tool_registry, functions, run_tool_call)

    messages2 = copy.deepcopy(messages)
    res2 = humboldt.chat_loop(client, args, messages2, tool_registry, functions, run_tool_call)

    assert res1 == res2
    assert messages1 == messages2

    # 3. check_and_install_dependencies
    mock_run = mocker.patch("subprocess.run")
    mocker.patch("importlib.util.find_spec", return_value=None)

    res1 = humboldt.check_and_install_dependencies()
    count1 = mock_run.call_count

    res2 = humboldt.check_and_install_dependencies()
    count2 = mock_run.call_count - count1

    assert res1 == res2
    assert count1 == count2

    # 4. execute_tool_loop
    args = mocker.MagicMock(max_steps=1, debug=False)
    messages = [{"role": "user", "content": "hello"}]
    mock_llm = mocker.patch("humboldt.call_llm_with_retry")
    mock_msg = mocker.MagicMock()
    mock_msg.choices = [mocker.MagicMock()]
    mock_msg.choices[0].message = mocker.MagicMock(content="Hello there!", function_call=None)
    mock_llm.return_value = mock_msg

    messages1 = copy.deepcopy(messages)
    res1 = humboldt.execute_tool_loop(client, args, messages1, functions, run_tool_call)

    messages2 = copy.deepcopy(messages)
    res2 = humboldt.execute_tool_loop(client, args, messages2, functions, run_tool_call)

    assert res1 == res2
    assert messages1 == messages2

    # 5. handle_direct_command
    registry = mocker.MagicMock()
    registry.invoke.return_value = "Result"

    cmd = "/geocode Paris"
    res1 = humboldt.handle_direct_command(cmd, registry)
    res2 = humboldt.handle_direct_command(cmd, registry)

    assert res1 == res2
    assert res1 is True

    # 6. is_package_installed
    mocker.patch("importlib.util.find_spec", return_value=mocker.MagicMock())
    pkg = "openai"

    res1 = humboldt.is_package_installed(copy.deepcopy(pkg))
    res2 = humboldt.is_package_installed(copy.deepcopy(pkg))

    assert res1 == res2

    # 7. main
    mocker.patch("humboldt.check_and_install_dependencies")
    mocker.patch("builtins.input", side_effect=["exit", "exit"])
    mocker.patch("sys.argv", ["humboldt.py"])
    mocker.patch("openai.OpenAI")
    mocker.patch("tool_registry.create_registry")

    res1 = humboldt.main()
    res2 = humboldt.main()

    assert res1 == res2
