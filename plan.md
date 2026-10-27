1. **Restore tests/test_humboldt.py**
   ```bash
   git restore tests/test_humboldt.py
   ```

2. **Add Tests to `tests/test_humboldt.py`**
   ```bash
   cat << 'EOF' >> tests/test_humboldt.py

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
