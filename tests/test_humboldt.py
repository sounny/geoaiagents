import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from humboldt import main

@pytest.mark.xfail(reason="Humboldt calls LLM for empty or whitespace-only input instead of a no-op")
def test_humboldt_empty_input(mocker, capsys, tmp_path):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    input_file = tmp_path / "input.txt"
    input_file.write_text("\n   \nexit\n")
    mock_input = mocker.patch('builtins.input', side_effect=input_file.read_text().splitlines())

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


@pytest.mark.skipif(sys.platform == "win32" or (hasattr(os, 'geteuid') and os.geteuid() == 0), reason="chmod read-only unsupported")
@pytest.mark.xfail(reason="pip install exits with SystemExit on read-only failure instead of clean fallback")
def test_check_and_install_dependencies_readonly(mocker, tmp_path):
    import os
    import humboldt
    ro_dir = tmp_path / "ro"
    ro_dir.mkdir()
    os.chmod(ro_dir, 0o555)

    mocker.patch('humboldt.is_package_installed', return_value=False)

    mock_reqs = "missing_package==1.0.0"
    mocker.patch('builtins.open', mocker.mock_open(read_data=mock_reqs))
    mocker.patch('os.path.exists', return_value=True)

    mocker.patch.dict(os.environ, {"PYTHONUSERBASE": str(ro_dir)})

    try:
        humboldt.check_and_install_dependencies()
    except Exception as e:
        pytest.xfail(f"Bug: unhandled exception {e}")
    except SystemExit as e:
        assert e.code == 1
        pytest.xfail("Bug: sys.exit(1) called on permission denied instead of clean fallback")

    pytest.fail("Expected failure or SystemExit")
