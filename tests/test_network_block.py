import pytest
import urllib.request

@pytest.mark.xfail(reason="Network blocks are not actually implemented yet.")
def test_network_block():
    """Verify that outbound network calls are blocked during tests."""
    with pytest.raises(Exception):
        urllib.request.urlopen("http://example.com", timeout=1)
