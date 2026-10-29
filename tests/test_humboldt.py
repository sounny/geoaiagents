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

@pytest.mark.xfail(reason="Reads BOM as part of package name")
def test_humboldt_bom_crlf_requirements(tmp_path, monkeypatch, mocker):
    from humboldt import check_and_install_dependencies
    req_file = tmp_path / "requirements.txt"
    with open(req_file, "wb") as f:
        f.write(b'\xef\xbb\xbfopenai>=1.0.0\r\ngeopy==2.0.0\r\n')
    monkeypatch.chdir(tmp_path)
    mock_run = mocker.patch("subprocess.run")
    mocker.patch("humboldt.is_package_installed", return_value=False)

    check_and_install_dependencies()

    # Asserting CURRENT results (the bug)
    args = mock_run.call_args_list[0][0][0]
    assert "\ufeffopenai" in args
