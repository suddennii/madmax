
'''
파일 목적 :
학습과목의 API 자동화 로직 구현

작성자 : 조대건 / 수정일 : 26.02.04

테스트 목적 :
-로그인 API의 정상/에러 응답을 검증한다.
-파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.

기타 주의 사항 :
'''

import pytest
from utils.config import CLASSROOM_ID, PAGE_SKIP, PAGE_COUNT, TARGET_COURSE, ORG_NAME, LECTURE_ID, DEFAULT_PARAMS, MATERIAL_QUIZ_ID
from utils.auth_manager import AuthManager
from utils.api_client import ApiClient
from utils.logger import get_logger

# === logger 설정 시작 ===
logger = get_logger(__file__)
# === logger 설정 끝 ===

# 학습과목 목록 조회 테스트
@pytest.mark.smoke
def test_get_lsub01():
    client = ApiClient(token = AuthManager.get_token(), url_type="classroom")
    
    try:
        # API 호출
        response = client.get(
            f"/classroom/{CLASSROOM_ID}/course",
            params={"skip":PAGE_SKIP, "count":PAGE_COUNT}
        )
        
        # 기본 검증
        assert client.status_code == 200
        assert isinstance(response, list)
        assert len(response) > 0
        
    except Exception as e:
        # 예외 발생 시 로그 기록
        logger.error(f"API 호출/검증 실패: {e}, URL: /classroom/{CLASSROOM_ID}/course, params={{'skip': PAGE_SKIP, 'count': PAGE_COUNT}}")

        # 테스트 실패 처리
        raise
    
# 학습과목 상세 목록 조회
@pytest.mark.smoke
def test_get_lsub02():
    client = ApiClient(token = AuthManager.get_token(), url_type="course")
    
    # 헤더에 (x-elice-org-name-short 추가)
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    try:
        # API 호출
        response = client.get(f"/lecture_page", params=DEFAULT_PARAMS)
        
        assert client.status_code == 200
        assert isinstance(response, list)
        
        if not isinstance(response, list):
            raise TypeError(f"Expected list, but got {type(response).__name__}")
        
        assert len(response) > 0, "응답 리스트가 비어 있습니다"
        logger.info(f"LSUB-02 성공: 데이터 개수={len(response)}")
    except AssertionError as e:
        logger.error(f"LSUB-02 검증 실패 (AssertionError): {e}, params={DEFAULT_PARAMS}")
        raise
    except TypeError as e:
        logger.error(f"LSUB-02 응답 구조 에러 (TypeError): {e}, params={DEFAULT_PARAMS}")
        raise
    except Exception as e:
        logger.error(f"LSUB-02 API 서버 또는 시스템 에러: {e}, params={DEFAULT_PARAMS}")
        raise

# 학습과목 상세 강의 조화
@pytest.mark.smoke
def test_get_lsub03():
    client = ApiClient(token = AuthManager.get_token(), url_type="course")
    
    # 헤더에 (x-elice-org-name-short 추가)
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    try:
        # API 호출
        response = client.get(f"/lecture/{LECTURE_ID}", params=DEFAULT_PARAMS)
        
        assert client.status_code == 200
        assert isinstance(response, dict)
        
        if not isinstance(response, dict):
            raise TypeError(f"Expected list, but got {type(response).__name__}")
        
        assert len(response) > 0, "응답 리스트가 비어 있습니다"
        logger.info(f"LSUB-03 성공: 데이터 개수={len(response)}")
    except AssertionError as e:
        logger.error(f"LSUB-03 검증 실패 (AssertionError): {e}, params={DEFAULT_PARAMS}")
        raise
    except TypeError as e:
        logger.error(f"LSUB-03 응답 구조 에러 (TypeError): {e}, params={DEFAULT_PARAMS}")
        raise
    except Exception as e:
        logger.error(f"LSUB-03 API 서버 또는 시스템 에러: {e}, params={DEFAULT_PARAMS}")
        raise
    

# SANDBOX 과목 존재 여부 확인
@pytest.mark.smoke
def test_get_lsub04():
    client = ApiClient(token = AuthManager.get_token(), url_type="classroom")
    
    try:
        # API 호출
        response = client.get(
            f"/classroom/{CLASSROOM_ID}/course",
            params={"skip":PAGE_SKIP, "count":PAGE_COUNT}
        )
        
        # 기본 검증
        assert client.status_code == 200
        assert isinstance(response, list)
        assert len(response) > 0
        
        # 특정 과목 여부 체크
        titles = [course["title"] for course in response]
        logger.info(f"status_code={client.status_code}, titles:{titles}")
        assert TARGET_COURSE in titles, f"{TARGET_COURSE} 과목이 존재하지 않습니다."
    
    except Exception as e:
        # 예외 발생 시 로그 기록
        logger.error(f"API 호출/검증 실패: {e}, URL: /classroom/{CLASSROOM_ID}/course, params={{'skip': PAGE_SKIP, 'count': PAGE_COUNT}}")

        # 테스트 실패 처리
        raise
    
# offset/count 페이징 동작 확인
@pytest.mark.smoke
@pytest.mark.parametrize("skip, count", [
    (0, 5), # 첫 번째 페이지, 5개 요청
    (5, 5)  # 두 번째 페이지, 그 다음 5개 요청
])
def test_get_lsub5(skip, count):
    client = ApiClient(token = AuthManager.get_token(), url_type="course")
    # 헤더에 (x-elice-org-name-short 추가)
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    # 전역 설정 복사
    params = DEFAULT_PARAMS.copy()
    # 페이징 테스트에 필요한 값으로 변경
    params.update({
        "skip": skip,
        "count": count
    })
    try:
        # API 호출
        response = client.get(f"/lecture_page", params=params)
        
        # 1 기본검증
        assert client.status_code == 200
        assert isinstance(response, list)
        
        if not isinstance(response, list):
            raise TypeError(f"Expected list, but got {type(response).__name__}")
        
        # 2 응답 개수가 요청한 count보다 작거나 같아야 함
        actual_count = len(response)
        assert actual_count <= count, f"요청한 count({count}) 보다 많은 데이터({actual_count})가 반환되었습니다."
        
        # 3 데이터가 존재할 경우 로그 기록
        if actual_count > 0:
            first_item_id = response[0].get("id")
            logger.info(f"LSUB-05 성공 [skip={skip}, count={count}]: 응답 개수={actual_count}, 첫번째 ID={first_item_id}")
        else:
            logger.warning(f"LSUB-05 경고 [skip={skip}]: 해당 페이지에 데이터가 없습니다.")
            
    except AssertionError as e:
        logger.error(f"LSUB-05 검증 실패 (AssertionError): {e}, params={DEFAULT_PARAMS}")
        raise
    except TypeError as e:
        logger.error(f"LSUB-05 응답 구조 에러 (TypeError): {e}, params={DEFAULT_PARAMS}")
        raise
    except Exception as e:
        logger.error(f"LSUB-05 API 서버 또는 시스템 에러: {e}, params={DEFAULT_PARAMS}")
        raise
    
# 잘못된 파라메터 입력시 오류처리
@pytest.mark.negative
@pytest.mark.parametrize("invalid_param, expected_status, description", [
    ({"count": "abc"}, 422, "문자열 count 값 전송"),
    ({"filter_lecture_id": 0}, 200, "존재하지 않는 lecture_id 전송"),
    ({"skip": -1}, 422, "음수 skip 값 전송")
])
def test_get_lsub6(invalid_param, expected_status, description):
    client = ApiClient(token=AuthManager.get_token(), url_type="course")
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    # 기본 파라미터 복사 후 잘못된 값으로 업데이트
    params = DEFAULT_PARAMS.copy()
    params.update(invalid_param)
    
    if expected_status >= 400:
        with pytest.raises(Exception) as excinfo:
            client.get("/lecture_page", params=params)
        
        # 에러 메시지에 기대하는 상태 코드가 포함되어 있는지 확인
        assert str(expected_status) in str(excinfo.value)
        logger.info(f"음성 테스트 성공 [{description}]: 기대한 {expected_status} 에러 발생")

    # --- 시나리오 B: 에러는 안 나지만 결과가 비어있어야 할 때 ---
    else:
        response = client.get("/lecture_page", params=params)
        
        assert client.status_code == expected_status
        assert isinstance(response, list)
        
        # 데이터가 0건이어야 함을 검증
        assert len(response) == 0, f"{description} 상황인데 데이터가 반환되었습니다."
        logger.info(f"음성 테스트 성공 [{description}]: 200 OK 및 빈 데이터 확인")
        
# 인증 정보 없이 호출
@pytest.mark.negative
@pytest.mark.parametrize("missing_type, description", [
    ("token", "인증 토큰(Authorization)이 없는 경우"),
    ("org_name", "필수 헤더(x-elice-org-name-short)가 없는 경우")
])
def test_get_lsub7(missing_type, description):
   
    # 1 클라이언트 생성 (토큰 누락 케이스인 경우 None 전달)
    token = None if missing_type == "token" else AuthManager.get_token()
    client = ApiClient(token=token, url_type="course")
    
    # 2 헤더 설정 
    if missing_type != "org_name":
        client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    else:
        # API Client 생성 시 기본적으로 들어갈 수 있는 헤더 제거 
        if "x-elice-org-name-short" in client.session.headers:
            del client.session.headers["x-elice-org-name-short"]

    try:
        with pytest.raises(Exception) as excinfo:
            client.get("/lecture_page", params=DEFAULT_PARAMS)
        
        error_msg = str(excinfo.value)
        
        
        assert "401" in error_msg or "403" in error_msg
        
        logger.info(f"성공: [{description}] 기대한 에러 발생 확인.. ({error_msg})")

    except AssertionError as e:
        logger.error(f"실패: [{description}] 에러가 발생하지 않았거나 상태 코드가 다릅니다. {e}")
        raise
    except Exception as e:
        logger.error(f"실패: [{description}] 예상치 못한 시스템 에러: {e}")
        raise
    
# 부하테스트 1 시험입장
@pytest.mark.smoke
def test_get_load_test01():
    client = ApiClient(token = AuthManager.get_token(), url_type="course")
    
    # 헤더에 (x-elice-org-name-short 추가)
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
     # 전역 설정 복사
    params = DEFAULT_PARAMS.copy()
    # 페이징 테스트에 필요한 값으로 변경
    params.update({
        "count": 1,
        "filter_is_opened": True,
        "elice_course_id": 768575
    })
    
    try:
        # API 호출
        response = client.get(f"/lecture", params=params)
        
        assert client.status_code == 200
        assert isinstance(response, list)
        
        if not isinstance(response, list):
            raise TypeError(f"Expected list, but got {type(response).__name__}")
        
        # assert len(response) > 0, "응답 리스트가 비어 있습니다"
        logger.info(f"LSUB-02 성공: 데이터 개수={len(response)}")
    except AssertionError as e:
        logger.error(f"LSUB-02 검증 실패 (AssertionError): {e}, params={DEFAULT_PARAMS}")
        raise
    except TypeError as e:
        logger.error(f"LSUB-02 응답 구조 에러 (TypeError): {e}, params={DEFAULT_PARAMS}")
        raise
    except Exception as e:
        logger.error(f"LSUB-02 API 서버 또는 시스템 에러: {e}, params={DEFAULT_PARAMS}")
        raise

# 부하테스트 2 응시
@pytest.mark.smoke
def test_get_load_test02():
    client = ApiClient(token = AuthManager.get_token(), url_type="rest")
    
    # 헤더에 (x-elice-org-name-short 추가)
    # client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    # 전역 설정 복사
    params = DEFAULT_PARAMS.copy()
    # # 페이징 테스트에 필요한 값으로 변경
    params.update({
        "material_quiz_id": 54716206
    })
    
    try:
        # API 호출
        response = client.get(f"/org/qatrack/material_quiz/get", params=params)
        
        assert client.status_code == 200
        assert isinstance(response, list)
        
        if not isinstance(response, list):
            raise TypeError(f"Expected list, but got {type(response).__name__}")
        
        # assert len(response) > 0, "응답 리스트가 비어 있습니다"
        logger.info(f"LSUB-02 성공: 데이터 개수={len(response)}")
    except AssertionError as e:
        logger.error(f"LSUB-02 검증 실패 (AssertionError): {e}, params={DEFAULT_PARAMS}")
        raise
    except TypeError as e:
        logger.error(f"LSUB-02 응답 구조 에러 (TypeError): {e}, params={DEFAULT_PARAMS}")
        raise
    except Exception as e:
        logger.error(f"LSUB-02 API 서버 또는 시스템 에러: {e}, params={DEFAULT_PARAMS}")
        raise