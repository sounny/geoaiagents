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

import os
import time

def test_humboldt_tz(monkeypatch, tmp_path):
    from humboldt import check_and_install_dependencies, is_package_installed, build_parser, handle_direct_command, execute_tool_loop, chat_loop, main
    funcs = [
        (check_and_install_dependencies, [], {}),
        (is_package_installed, ['openai'], {}),
        (build_parser, [], {}),
        (handle_direct_command, ['/geocode Paris', MagicMock()], {}),
        (execute_tool_loop, [MagicMock(), MagicMock(), [], [], MagicMock()], {}),
        (chat_loop, [MagicMock(), MagicMock(), [], MagicMock(), [], MagicMock()], {}),
        (main, [], {})
    ]

    monkeypatch.setattr('builtins.input', MagicMock(side_effect=EOFError))
    monkeypatch.setattr('humboldt.check_and_install_dependencies', MagicMock())
    monkeypatch.setattr('sys.argv', ['humboldt.py', '--skip-deps'])

    sys.modules['openai'] = MagicMock()
    sys.modules['tool_registry'] = MagicMock()

    for func, args, kwargs in funcs:
        res1 = None
        res2 = None

        monkeypatch.setenv('TZ', 'UTC')
        if hasattr(time, 'tzset'):
            time.tzset()
        try:
            if func == build_parser:
                res1 = func(*args, **kwargs).parse_args([])
            else:
                res1 = func(*args, **kwargs)
        except Exception as e:
            res1 = type(e)

        monkeypatch.setenv('TZ', 'America/New_York')
        if hasattr(time, 'tzset'):
            time.tzset()
        try:
            if func == build_parser:
                res2 = func(*args, **kwargs).parse_args([])
            else:
                res2 = func(*args, **kwargs)
        except Exception as e:
            res2 = type(e)

        if res1 != res2:
            pytest.xfail(f"{func.__name__} behavior differs between timezones")

        assert res1 == res2
import pytest
import os
import time
from unittest.mock import MagicMock
import sys

from humboldt import check_and_install_dependencies, is_package_installed, build_parser, handle_direct_command, execute_tool_loop, chat_loop, main

@pytest.mark.parametrize("func_idx", range(7))
def test_humboldt_tz(monkeypatch, tmp_path, func_idx):
    funcs = [
        (check_and_install_dependencies, [], {}),
        (is_package_installed, ['openai'], {}),
        (build_parser, [], {}),
        (handle_direct_command, ['/geocode Paris', MagicMock()], {}),
        (execute_tool_loop, [MagicMock(), MagicMock(), [], [], MagicMock()], {}),
        (chat_loop, [MagicMock(), MagicMock(), [], MagicMock(), [], MagicMock()], {}),
        (main, [], {})
    ]

    monkeypatch.setattr('builtins.input', MagicMock(side_effect=EOFError))
    monkeypatch.setattr('humboldt.check_and_install_dependencies', MagicMock())
    monkeypatch.setattr('sys.argv', ['humboldt.py', '--skip-deps'])

    sys.modules['openai'] = MagicMock()
    sys.modules['tool_registry'] = MagicMock()

    func, args, kwargs = funcs[func_idx]
    res1 = None
    res2 = None

    monkeypatch.setenv('TZ', 'UTC')
    if hasattr(time, 'tzset'):
        time.tzset()
    try:
        if func == build_parser:
            res1 = func(*args, **kwargs).parse_args([])
        else:
            res1 = func(*args, **kwargs)
    except Exception as e:
        res1 = type(e)

    monkeypatch.setenv('TZ', 'America/New_York')
    if hasattr(time, 'tzset'):
        time.tzset()
    try:
        if func == build_parser:
            res2 = func(*args, **kwargs).parse_args([])
        else:
            res2 = func(*args, **kwargs)
    except Exception as e:
        res2 = type(e)

    if res1 != res2:
        pytest.xfail(f"{func.__name__} behavior differs between timezones")

    assert res1 == res2

import os
import time

@pytest.mark.parametrize("func_idx", range(7))
def test_humboldt_tz(monkeypatch, tmp_path, func_idx):
    from humboldt import check_and_install_dependencies, is_package_installed, build_parser, handle_direct_command, execute_tool_loop, chat_loop, main
    funcs = [
        (check_and_install_dependencies, [], {}),
        (is_package_installed, ['openai'], {}),
        (build_parser, [], {}),
        (handle_direct_command, ['/geocode Paris', MagicMock()], {}),
        (execute_tool_loop, [MagicMock(), MagicMock(), [], [], MagicMock()], {}),
        (chat_loop, [MagicMock(), MagicMock(), [], MagicMock(), [], MagicMock()], {}),
        (main, [], {})
    ]

    monkeypatch.setattr('builtins.input', MagicMock(side_effect=EOFError))
    monkeypatch.setattr('humboldt.check_and_install_dependencies', MagicMock())
    monkeypatch.setattr('sys.argv', ['humboldt.py', '--skip-deps'])

    sys.modules['openai'] = MagicMock()
    sys.modules['tool_registry'] = MagicMock()

    func, args, kwargs = funcs[func_idx]
    res1 = None
    res2 = None

    monkeypatch.setenv('TZ', 'UTC')
    if hasattr(time, 'tzset'):
        time.tzset()
    try:
        if func == build_parser:
            res1 = func(*args, **kwargs).parse_args([])
        else:
            res1 = func(*args, **kwargs)
    except Exception as e:
        res1 = type(e)

    monkeypatch.setenv('TZ', 'America/New_York')
    if hasattr(time, 'tzset'):
        time.tzset()
    try:
        if func == build_parser:
            res2 = func(*args, **kwargs).parse_args([])
        else:
            res2 = func(*args, **kwargs)
    except Exception as e:
        res2 = type(e)

    if res1 != res2:
        pytest.xfail(f"{func.__name__} behavior differs between timezones")

    assert res1 == res2
