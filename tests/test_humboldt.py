import pytest
from humboldt import is_package_installed

def test_is_package_installed_fake_package():
    assert is_package_installed('definitely_not_a_real_pkg_xyz_9f3') is False

def test_is_package_installed_openai():
    # Should reflect whether openai is importable (True or False is fine)
    result = is_package_installed('openai')
    assert isinstance(result, bool)
