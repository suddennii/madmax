
import pytest
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient

@pytest.fixture(scope="session")
def token():
    return AuthManager.get_token()

@pytest.fixture
def client(request, token):
    base_url = getattr(request, "param", None)
    client = ApiClient(token=token, base_url=base_url)
    return client
