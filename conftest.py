import os

import pytest
import requests

from mock_server import server as mock_server

LIVE_URL = "https://jsonplaceholder.typicode.com"


def pytest_addoption(parser):
    parser.addoption("--base-url", default=os.getenv("BASE_URL", LIVE_URL),
                     help="API base URL (default: JSONPlaceholder)")
    parser.addoption("--mock", action="store_true",
                     help="Run against the bundled offline mock server")


@pytest.fixture(scope="session")
def base_url(request):
    if request.config.getoption("--mock"):
        srv, url = mock_server.start()
        yield url
        srv.shutdown()
    else:
        yield request.config.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def api(base_url):
    """requests.Session that prefixes every path with the base URL and has a timeout."""

    class Client(requests.Session):
        def request(self, method, url, **kwargs):
            kwargs.setdefault("timeout", 10)
            if url.startswith("/"):
                url = base_url + url
            return super().request(method, url, **kwargs)

    client = Client()
    client.headers.update({"Accept": "application/json"})
    yield client
    client.close()
