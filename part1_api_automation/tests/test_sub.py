import pytest
from utils.config import QATRACK_URL, TIMEOUT, CLASSROOM_ID, CLASSROOM_URL
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.logger import get_logger

# === logger 설정 시작 ===
logger = get_logger(__file__)
# === logger 설정 끝 ===

# 학습과목 목록 조회 테스트
def test_get_course_list():
    token = AuthManager.get_token()
    client = ApiClient(token=token, base_url=CLASSROOM_URL)
    response = client.get(
        f"/classroom/{CLASSROOM_ID}/course",
        params={"skip":0, "count":20}
    )
    print("ststus_code", client.status_code)
    
    assert isinstance(response, list)
    assert len(response) > 0
    
    titles = [course["title"] for course in response]
    logger.info(f"titles:{titles}")
    assert "SANDBOX" in titles