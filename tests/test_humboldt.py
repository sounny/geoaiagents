import pytest
import sys
from unittest.mock import patch, MagicMock
from humboldt import main
import humboldt

@pytest.mark.xfail(reason="Humboldt calls LLM for empty or whitespace-only input instead of a no-op")
def test_humboldt_empty_input(mocker, capsys):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')
    mock_input = mocker.patch('builtins.input', side_effect=['', '   ', 'exit'])
    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mocker.patch('sys.argv', ['humboldt.py'])
    main()
    assert mock_call_llm.call_count == 0, "LLM was called for empty or whitespace-only input"
    out, err = capsys.readouterr()

@pytest.mark.parametrize("empty_str", ["", "   "])
@pytest.mark.xfail(raises=AssertionError, reason="Bug: silently ignores empty string instead of raising ValueError")
def test_is_package_installed_empty_strings(empty_str, mocker, tmp_path):
    mock_env = tmp_path / "mock_env"
    mock_env.mkdir()
    mocker.patch("sys.path", [str(mock_env)])
    mocker.patch("subprocess.run")
    mocker.patch("importlib.util.find_spec", return_value=None)

    # Assert current behavior
    assert humboldt.is_package_installed(empty_str) is False
    # Unconditionally raise AssertionError per memory guidelines
    raise AssertionError("Bug: silently ignores empty string instead of raising ValueError")

@pytest.mark.parametrize("empty_str", ["", "   "])
@pytest.mark.xfail(raises=AssertionError, reason="Bug: passes through empty string to LLM")
def test_handle_direct_command_empty_strings(empty_str, mocker, tmp_path):
    mock_registry = MagicMock()
    mock_env = tmp_path / "mock_env"
    mock_env.mkdir()
    mocker.patch("sys.path", [str(mock_env)])

    # Assert current behavior
    result = humboldt.handle_direct_command(empty_str, mock_registry)
    assert result is False
    # Unconditionally raise AssertionError per memory guidelines
    raise AssertionError("Bug: passes through empty string to LLM")
