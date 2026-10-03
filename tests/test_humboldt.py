import pytest
import importlib.util
from humboldt import is_package_installed

def test_is_package_installed_empty_and_mapping(mocker):
    # The prompt asked to stub install side effects - do not run pip
    # We will mock subprocess.run and subprocess.check_call just in case
    mocker.patch('subprocess.run')
    mocker.patch('subprocess.check_call')

    # Empty string should be False safely
    assert is_package_installed('') is False

    # 'definitely_not_a_real_pkg_zz9' should be False
    assert is_package_installed('definitely_not_a_real_pkg_zz9') is False

    # 'openai' maps to 'openai' and should return True if it is importable, False otherwise.
    # It shouldn't crash, and should return a bool.
    # The actual result will match find_spec('openai') is not None.
    expected_openai = importlib.util.find_spec('openai') is not None
    result = is_package_installed('openai')
    assert isinstance(result, bool)
    assert result is expected_openai
