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

@pytest.mark.skipif(sys.platform.startswith("win"), reason="Windows")
@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="Root")
@pytest.mark.xfail(raises=PermissionError, reason="looks like a bug")
def test_check_and_install_dependencies_permission(tmp_path, monkeypatch):
    with patch("humboldt.subprocess.run"):
        req = tmp_path / "requirements.txt"
        req.write_text("pytest\n")
        req.chmod(0)
        monkeypatch.chdir(tmp_path)
        from humboldt import check_and_install_dependencies
        check_and_install_dependencies()
