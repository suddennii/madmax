"""
2025-02-05 심다영
board_api에 사용할 fixture 입력
"""


import pytest
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.board_api import BoardAPI
import os
import json

@pytest.fixture(scope="session")
def token():
    return AuthManager.get_token()

@pytest.fixture
def client(token):
    return ApiClient(token=token)

@pytest.fixture
def student_course_parmas():
    path=os.path.join(
        "test_data", "student_course.json"
    )
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
@pytest.fixture
def board_api(client):
    return BoardAPI(client)


