"""
파일 목적 : API 테스트 공통 설정

**작성자** : 박지우 / **작성일** : 26.02.04
**작성자** : 박지우 / **수정일** : 26.02.09
**작성자** : 심다영 / **수정일** : 26.02.10

**파일 목적 :**
- 대시보드 API 테스트에 필요한 공통 fixture 정의
- 인증 토큰 발급 및 None 토큰 환경 제공
- url_type(dash/classroom 등)에 따른 ApiClient 생성
- BoardAPI 래퍼 객체 제공

기타 주의 사항 : 없음
"""
import pytest
import requests
import os # 심다영 추가
import json # 심다영 추가

from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.board_api import BoardAPI
from utils.config import SESSION_KEY, ORG_NAME  # 심다영 추가


# ---------------------------------------------------------
# 인증 토큰 관련 Fixture
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def token():
    return AuthManager.get_token()

@pytest.fixture(scope="session")
def no_token():
    return None

# ---------------------------------------------------------
# API Client Factory (일반 API용) # 심다영 추가
# ---------------------------------------------------------
@pytest.fixture
def client_factory():
    def _create(token, url_type):
        return ApiClient(token=token, url_type=url_type)
    return _create

# ---------------------------------------------------------
# Board API Wrapper (게시판 API용) # 심다영 추가
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def client(token):
    """
    BoardAPI에 주입할 Session 객체 생성
    - 헤더(Bearer Token)와 쿠키(_session_key)를 모두 설정합니다.
    """
    session = requests.Session()
    
    # 1. 공통 헤더
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",  # 헤더 인증
        "x-elice-org-name-short": ORG_NAME
    })

    # 2. 쿠키 인증 (SESSION_KEY 사용)
    if SESSION_KEY:
        session.cookies.set("_session_key", SESSION_KEY)

    # 3. status_code 저장을 위한 속성 초기화
    session.status_code = None 

    yield session
    session.close()

@pytest.fixture(scope="session")
def board_api(client):
    """
    BoardAPI 인스턴스 생성
    - 위에서 만든 client(Session)를 주입받습니다.
    """
    return BoardAPI(client=client)

# ---------------------------------------------------------
# 테스트 데이터 (선택 사항) # 심다영 추가
# ---------------------------------------------------------
@pytest.fixture
def student_course_params():
    path = os.path.join("test_data", "student_course.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}