import pytest
from utils.config import QATRACK_URL, TIMEOUT, CLASSROOM_ID, CLASSROOM_URL, PAGE_SKIP, PAGE_COUNT, TARGET_COURSE
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.logger import get_logger

# === logger 설정 시작 ===
logger = get_logger(__file__)
# === logger 설정 끝 ===

# 학습과목 목록 조회 테스트
@pytest.mark.smoke
@pytest.mark.parametrize("client", [CLASSROOM_URL], indirect=True)
def test_get_course_list(client):
    try:
        # API 호출
        response = client.get(f"/classroom/{CLASSROOM_ID}/course", params={"skip":PAGE_SKIP, "count":PAGE_COUNT})
        
        # 기본 검증
        assert client.status_code == 200
        assert isinstance(response, list)
        assert len(response) > 0
        
        titles = [course["title"] for course in response]
        logger.info(f"status_code={client.status_code}, titles:{titles}")
        assert TARGET_COURSE in titles, f"{TARGET_COURSE} 과목이 존재하지 않습니다."
    
    except Exception as e:
        # 예외 발생 시 로그 기록
        logger.error(f"API 호출/검증 실패: {e}, URL: /classroom/{CLASSROOM_ID}/course, params={{'skip': PAGE_SKIP, 'count': PAGE_COUNT}}")

        # 테스트 실패 처리
        raise