from humboldt import is_package_installed

def test_is_package_installed_existing():
    assert is_package_installed("json") is True

def test_is_package_installed_nonsense():
    assert is_package_installed("some_nonsense_package_that_does_not_exist_12345") is False
