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



NON_ASCII_STRINGS = [
    "café",
    "你好",
    "🌍",
    "مرحبا",
]

@pytest.mark.parametrize("text", NON_ASCII_STRINGS)
def test_is_package_installed_non_ascii(text, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from humboldt import is_package_installed
    # is_package_installed just checks importlib.util.find_spec, no network/fs required
    result = is_package_installed(text)
    assert result is False

@pytest.mark.parametrize("text", NON_ASCII_STRINGS)
def test_handle_direct_command_non_ascii(text, tmp_path, mocker, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from humboldt import handle_direct_command
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "MOCKED_RESPONSE"

    assert handle_direct_command(text, mock_registry) is False

    for cmd in ["/geocode ", "/reverse ", "/dms ", "/distance "]:
        assert handle_direct_command(f"{cmd}{text}", mock_registry) is True

        if cmd == "/geocode ":
            mock_registry.invoke.assert_called_with("geocode_locations", {"locations": text})
        elif cmd == "/reverse ":
            mock_registry.invoke.assert_called_with("reverse_geocode_coordinates", {"coordinates": text})
        elif cmd == "/dms ":
            mock_registry.invoke.assert_called_with("convert_dd_to_dms", {"coordinates": text})
        elif cmd == "/distance ":
            mock_registry.invoke.assert_called_with("calculate_distance", {"coordinates": text})

@pytest.mark.parametrize("text", NON_ASCII_STRINGS)
def test_call_llm_with_retry_non_ascii(text, tmp_path, mocker, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from llm_utils import call_llm_with_retry

    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    # Assert current behavior: success without exception
    result = call_llm_with_retry(mock_client, messages=[{"role": "user", "content": text}])
    assert result == mock_response
    mock_client.chat.completions.create.assert_called_with(messages=[{"role": "user", "content": text}])
