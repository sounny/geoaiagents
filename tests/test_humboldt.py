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
import os

def test_humboldt_main_public_functions_determinism(mocker, capsys):
    random.seed(42)

    # mock external calls
    mock_subprocess = mocker.patch('subprocess.run')
    mock_llm = mocker.patch('humboldt.call_llm_with_retry')

    mock_llm_response = mocker.MagicMock()
    mock_llm_response.choices = [mocker.MagicMock()]
    mock_llm_response.choices[0].message.content = "mock response"
    mock_llm_response.choices[0].message.function_call = None
    mock_llm.return_value = mock_llm_response

    mock_tool_registry = mocker.MagicMock()
    mock_tool_registry.invoke.return_value = "mock_tool_result"

    # 1. is_package_installed
    import humboldt
    res1 = humboldt.is_package_installed('openai')
    res2 = humboldt.is_package_installed('openai')
    assert res1 == res2

    # 2. build_parser
    mocker.patch.dict(os.environ, {"OPENAI_BASE_URL": "mock_env", "OPENAI_API_KEY": "mock_env", "HUMBOLDT_MAX_STEPS": "3"})
    p1 = humboldt.build_parser()
    p2 = humboldt.build_parser()
    assert p1.parse_known_args([]) == p2.parse_known_args([])

    # 3. handle_direct_command
    r1 = humboldt.handle_direct_command("/geocode Paris", mock_tool_registry)
    out1 = capsys.readouterr().out
    r2 = humboldt.handle_direct_command("/geocode Paris", mock_tool_registry)
    out2 = capsys.readouterr().out
    assert r1 == r2
    assert out1 == out2

    # 4. execute_tool_loop
    args = mocker.MagicMock()
    args.max_steps = 1
    args.debug = False
    args.model = "mock-model"

    m1 = [{"role": "user", "content": "hello"}]
    humboldt.execute_tool_loop(None, args, m1, [], lambda x,y: None)
    out_loop1 = capsys.readouterr().out

    m2 = [{"role": "user", "content": "hello"}]
    humboldt.execute_tool_loop(None, args, m2, [], lambda x,y: None)
    out_loop2 = capsys.readouterr().out

    assert m1 == m2
    assert out_loop1 == out_loop2

    # 5. check_and_install_dependencies
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data="openai==1.0\n"))
    # is_package_installed needs to be patched just for this block if we want it to return False
    with mocker.patch('humboldt.is_package_installed', return_value=False):
        humboldt.check_and_install_dependencies()
        out_deps1 = capsys.readouterr().out

        humboldt.check_and_install_dependencies()
        out_deps2 = capsys.readouterr().out

        assert out_deps1 == out_deps2

    # 6. chat_loop
    mocker.patch('builtins.input', side_effect=['hello', 'exit', 'hello', 'exit'])
    m_chat1 = []
    humboldt.chat_loop(None, args, m_chat1, mock_tool_registry, [], lambda x,y: None)
    out_chat1 = capsys.readouterr().out

    m_chat2 = []
    humboldt.chat_loop(None, args, m_chat2, mock_tool_registry, [], lambda x,y: None)
    out_chat2 = capsys.readouterr().out

    assert m_chat1 == m_chat2
    assert out_chat1 == out_chat2
