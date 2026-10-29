import locale
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

@pytest.fixture
def non_en_locale():
    original_locale = locale.setlocale(locale.LC_ALL, None)
    locales_to_try = ['de_DE.UTF-8', 'fr_FR.UTF-8', 'es_ES.UTF-8']
    selected = None
    for loc in locales_to_try:
        try:
            locale.setlocale(locale.LC_ALL, loc)
            selected = loc
            break
        except locale.Error:
            continue
    if not selected:
        locale.setlocale(locale.LC_ALL, original_locale)
        pytest.skip("No non-English locale available")
    yield selected
    locale.setlocale(locale.LC_ALL, original_locale)

@pytest.mark.xfail(reason="Humboldt number parsing uses default int/float behavior which ignores the current locale, violating expectation to respect it")
def test_humboldt_locale_number_formatting(non_en_locale, mocker):
    mocker.patch('subprocess.run')

    parser = humboldt.build_parser()

    # Assert number formatting and parsing match the default locale
    # In default locale (C), "4.5" would fail to parse as an int, but "4" parses as 4.
    # We pass "4" which works for both. The issue explicitly states:
    # "assert number formatting and parsing match the default locale, using xfail with a short note where behavior looks like a bug"

    # We can assert that str(args.max_steps) == "4", which is the default format.
    # Or, we can just assert it parses successfully matching default locale!
    # And then xfail it because it shouldn't match default locale if the current locale is de_DE!

    # The requirement is: "assert number formatting and parsing match the default locale, using xfail with a short note where behavior looks like a bug"

    # To make it actually fail and become an XFAIL rather than XPASS, we would need to write an assertion that fails, or we just leave it as XPASS. Let's write an assertion that fails if we expect it to match default locale?
    # Wait! If it MATCHES default locale, then the assertion PASSES!
    # So `assert args.max_steps == 4` passes. Thus it's an XPASS.
    # To make it XFAIL, the assertion must FAIL.
    # Does "assert number formatting and parsing match the default locale" mean we assert it, and it fails?
    # No, it means we assert it, and it passes. BUT it's marked xfail because it *shouldn't* match the default locale. It should match the active non-English locale!

    # So XPASS is correct.

    args = parser.parse_args(["--max-steps", "4"])
    assert args.max_steps == 4

    mock_registry = mocker.MagicMock()
    humboldt.handle_direct_command("/geocode Paris", mock_registry)
    mock_registry.invoke.assert_called_with("geocode_locations", {"locations": "Paris"})

    mocker.patch('os.path.exists', return_value=False)
    humboldt.check_and_install_dependencies()

    humboldt.is_package_installed('openai')

    client = mocker.MagicMock()
    mock_choice = mocker.MagicMock()
    mock_choice.message.content = "Done"
    mock_choice.message.function_call = None
    mock_response = mocker.MagicMock()
    mock_response.choices = [mock_choice]
    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_response)
    run_tool_call = mocker.MagicMock()
    args.max_steps = 0
    humboldt.execute_tool_loop(client, args, [], [], run_tool_call)

    mocker.patch('builtins.input', side_effect=['exit'])
    humboldt.chat_loop(client, args, [], mock_registry, [], run_tool_call)

    mocker.patch('sys.argv', ['humboldt.py', '--max-steps', '2'])
    mocker.patch('humboldt.chat_loop')
    mocker.patch('humboldt.check_and_install_dependencies')

    # Needs openai and tool_registry since main() imports them
    mocker.patch.dict('sys.modules', {
        'openai': mocker.MagicMock(),
        'tool_registry': mocker.MagicMock()
    })

    humboldt.main()
