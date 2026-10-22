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

def test_check_and_install_dependencies_failure(mocker, capsys, tmp_path):
    import subprocess
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data="nonexistent-pkg==1.0\n"))
    mocker.patch('humboldt.is_package_installed', return_value=False)

    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, cmd="mock cmd", output="mock out", stderr="mock err")
    mocker.patch('subprocess.run', side_effect=mock_run)

    with pytest.raises(SystemExit) as excinfo:
        from humboldt import check_and_install_dependencies
        check_and_install_dependencies()

    assert excinfo.value.code == 1

    out, err = capsys.readouterr()
    assert out != ""
    assert "nonexistent-pkg" in out

def test_main_import_error(mocker, capsys):
    mocker.patch('sys.argv', ['humboldt.py'])
    mocker.patch('humboldt.check_and_install_dependencies')

    # For a module imported via `importlib` or at module level, mocking __import__ works.
    # However, since `humboldt.py` has `main()` which attempts to do:
    #     from openai import OpenAI
    #     from tool_registry import create_registry
    # We can patch builtins.__import__ specifically for openai.

    original_import = __import__
    def mock_import(name, *args, **kwargs):
        if name == 'openai':
            raise ImportError("No module named 'openai'")
        return original_import(name, *args, **kwargs)

    mocker.patch('builtins.__import__', side_effect=mock_import)

    import runpy

    with pytest.raises(SystemExit) as excinfo:
        # Better to run the module directly to ensure it catches the top-level import
        # actually humboldt.py delays import to main(). So calling main() works.
        from humboldt import main
        main()

    assert excinfo.value.code == 1

    out, err = capsys.readouterr()
    assert out != ""
    assert "Error importing required modules" in out
    assert "No module named 'openai'" in out
