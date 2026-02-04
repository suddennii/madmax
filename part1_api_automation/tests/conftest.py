
import pytest
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient

@pytest.fixture(scope="session")
def token():
    return AuthManager.get_token()

@pytest.fixture
def client(token):
    return ApiClient(token=token)
