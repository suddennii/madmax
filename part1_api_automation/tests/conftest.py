"""
파일 목적 : API 테스트 공통 설정

**작성자** : 박지우 / **작성일** : 26.02.04
**작성자** : 박지우 / **수정일** : 26.02.09

**파일 목적 :**
- 대시보드 API 테스트에 필요한 공통 fixture 정의
- 인증 토큰 발급 및 None 토큰 환경 제공
- url_type(dash/classroom 등)에 따른 ApiClient 생성
- BoardAPI 래퍼 객체 제공

기타 주의 사항 : 없음
"""
import pytest
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.board_api import BoardAPI

# ---------------------------------------------------------
# 인증 토큰 관련 Fixture
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def token():
    # 정상 인증 토큰
    return AuthManager.get_token()

@pytest.fixture(scope="session")
def no_token():
    # 토큰 없음 테스트
    return None

# ---------------------------------------------------------
# API Client Factory
# url_type(dash/classroom 등)에 따라 ApiClient 생성
# ---------------------------------------------------------
@pytest.fixture
def client_factory():
    def _create(token, url_type):
        return ApiClient(token=token, url_type=url_type)
    return _create

# ---------------------------------------------------------
# Board API Wrapper
# ---------------------------------------------------------
@pytest.fixture
def board_api(client):
    return BoardAPI(client)


