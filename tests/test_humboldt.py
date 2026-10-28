import humboldt
from unittest.mock import mock_open
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

def test_check_and_install_dependencies_identical(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data="openai==1.0\n"))
    mocker.patch('humboldt.is_package_installed', return_value=True)
    mocker.patch('subprocess.run')

    out1 = humboldt.check_and_install_dependencies()
    out2 = humboldt.check_and_install_dependencies()
    assert out1 == out2

def test_is_package_installed_identical(mocker):
    mocker.patch('importlib.util.find_spec', return_value=MagicMock())
    out1 = humboldt.is_package_installed("geopy")
    out2 = humboldt.is_package_installed("geopy")
    assert out1 == out2

@pytest.mark.xfail(reason="Returns new ArgumentParser instance each time, which does not implement __eq__")
def test_build_parser_identical(mocker):
    mocker.patch('os.getenv', return_value="dummy")
    out1 = humboldt.build_parser()
    out2 = humboldt.build_parser()
    assert out1 == out2

def test_handle_direct_command_identical(mocker):
    mock_registry = MagicMock()
    mock_registry.invoke.return_value = "Mock result"

    out1 = humboldt.handle_direct_command("/geocode Paris", mock_registry)
    out2 = humboldt.handle_direct_command("/geocode Paris", mock_registry)
    assert out1 == out2
    assert out1 is True

def test_execute_tool_loop_identical(mocker):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 1
    args.model = "test"
    args.debug = False

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Test content"
    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)

    messages1 = []
    functions = []
    run_tool_call = MagicMock()

    out1 = humboldt.execute_tool_loop(client, args, messages1, functions, run_tool_call)

    messages2 = []
    out2 = humboldt.execute_tool_loop(client, args, messages2, functions, run_tool_call)

    assert out1 == out2

def test_chat_loop_identical(mocker):
    client = MagicMock()
    args = MagicMock()
    messages1 = []
    messages2 = []
    tool_registry = MagicMock()
    functions = []
    run_tool_call = MagicMock()

    mocker.patch('builtins.input', side_effect=['exit', 'exit'])

    out1 = humboldt.chat_loop(client, args, messages1, tool_registry, functions, run_tool_call)
    out2 = humboldt.chat_loop(client, args, messages2, tool_registry, functions, run_tool_call)

    assert out1 == out2

def test_main_identical(mocker):
    mock_parser = MagicMock()
    mock_parser.parse_known_args.return_value = (MagicMock(skip_deps=True), [])
    mocker.patch('humboldt.build_parser', return_value=mock_parser)
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('sys.argv', ['humboldt.py'])

    mocker.patch.dict('sys.modules', {
        'openai': MagicMock(),
        'tool_registry': MagicMock()
    })

    mocker.patch('humboldt.chat_loop')

    out1 = humboldt.main()
    out2 = humboldt.main()
    assert out1 == out2
