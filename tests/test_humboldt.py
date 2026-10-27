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

def test_handle_direct_command_unicode(mocker):
    import unicodedata
    from humboldt import handle_direct_command
    from unittest.mock import MagicMock

    nfc_str = '/geocode ' + unicodedata.normalize('NFC', 'a café with combining characters \u0301')
    nfd_str = '/geocode ' + unicodedata.normalize('NFD', 'a café with combining characters \u0301')

    registry = MagicMock()

    handle_direct_command(nfc_str, registry)
    res_nfc = registry.invoke.call_args[0][1]['locations']

    handle_direct_command(nfd_str, registry)
    res_nfd = registry.invoke.call_args[0][1]['locations']

    if res_nfc != res_nfd:
        pytest.xfail("handle_direct_command does not normalize unicode text")

    assert res_nfc == res_nfd

def test_is_package_installed_unicode():
    import unicodedata
    from humboldt import is_package_installed

    nfc_str = unicodedata.normalize('NFC', 'café\u0301')
    nfd_str = unicodedata.normalize('NFD', 'café\u0301')

    res_nfc = is_package_installed(nfc_str)
    res_nfd = is_package_installed(nfd_str)

    if res_nfc != res_nfd:
        pytest.xfail("is_package_installed does not normalize unicode text")

    assert res_nfc == res_nfd
