import socket
import pytest

class NetworkAccessBlockedError(Exception):
    pass

@pytest.fixture(autouse=True)
def block_network(request, monkeypatch):
    if request.node.get_closest_marker('allow_network'):
        return

    original_connect = socket.socket.connect

    def mock_connect(self, address):
        raise NetworkAccessBlockedError(
            f"Network access is blocked during tests. "
            f"Attempted to connect to {address}. "
            f"Use @pytest.mark.allow_network to opt out."
        )

    monkeypatch.setattr("socket.socket.connect", mock_connect)
