'''
파일 목적 : 
수업일정 API 기능 검증 코드
작성자 : 김건후 / 작성일 : 26.02.04
작성자 : 김건후 / 수정일 : 26.02.10
테스트 목적 : 
-수업일정 API의 정상 응답 및 데이터 정합성을 검증한다.
'''

import pytest
import yaml
import os
from utils.api_client import ApiClient
from utils.config import CLASSROOM_ID, ORG_NAME
from utils.logger import logger

# ---------------------------------------------------------
# [데이터 로드 로직]
# ---------------------------------------------------------
def load_test_data():
    """
    프로젝트 루트의 test_data/schedule_data.yml 파일을 읽어옵니다.
    """
    # 현재 파일(tests/test_schedule.py)의 상위의 상위 폴더(루트)를 찾습니다.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 루트에 있는 'test_data' 폴더 안의 파일을 가리킵니다.
    file_path = os.path.join(base_dir, "test_data", "schedule_data.yml")
    
    if not os.path.exists(file_path):
        # 파일이 없으면 에러를 내서 실행을 멈춥니다.
        raise FileNotFoundError(f"YAML 파일을 찾을 수 없습니다! 위치 확인: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


data_all = load_test_data()

# ---------------------------------------------------------
# [헬퍼 함수]
# ---------------------------------------------------------

def _is_title_in_list(target_list, search_title):
    """
    [헬퍼] 리스트 내 항목들 중 겉 또는 내부 lecture 객체에 특정 제목이 포함되어 있는지 확인합니다.
    """
    for item in target_list:
        top_title = item.get("title", "")
        lecture_title = item.get("lecture", {}).get("title", "") if item.get("lecture") else ""
        
        if search_title in top_title or search_title in lecture_title:
            return True
    return False

# 클라이언트 생성 팩토리 피처
@pytest.fixture
def api_client_factory(token):
    """
    ApiClient 생성 및 공통 헤더 설정을 담당하는 팩토리 함수를 반환합니다.
    """
    def _create_client(url_type="classroom", custom_token=None):
        target_token = custom_token if custom_token else token
        client = ApiClient(token=target_token, url_type=url_type)
        client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
        return client
    return _create_client

#자동화코드 [1] ---------------------------------------
@pytest.mark.course
@pytest.mark.parametrize("data", data_all["schedule_list"])
def test_get_schedule_list(api_client_factory, data):
    """
    수업 일정 조회 기능 검증 (TC별 맞춤 날짜 검증 포함)
    """
    tc_id = data['tc_id']
    logger.info(f"{tc_id} 실행: {data['desc']}")

    client = api_client_factory(url_type="classroom")
    params = {
        "classroom_id": CLASSROOM_ID,
        "dt_start_ge": data['start_ge'],
        "dt_start_le": data['start_le'],
        "count": 40,
    }

    response = client.get("/schedule", params=params)

    assert client.status_code == 200, f"[{tc_id}] 응답 코드 에러: {client.status_code}"
    assert isinstance(response, list), f"[{tc_id}] 응답 데이터 형식 에러"
    
    if len(response) > 0:
        first_item = response[0]
        assert "id" in first_item and "dt_start" in first_item, f"[{tc_id}] 필수 필드 누락"
        if "tags" in first_item and "classroom_id" in first_item["tags"]:
            assert first_item["tags"]["classroom_id"] == CLASSROOM_ID, f"[{tc_id}] ID 불일치"

        if data['target_date']:
            found_target = any(data['target_date'] in s.get("dt_start", "") for s in response)
            assert found_target, f"[{tc_id}] {data['target_date']} 수업 데이터가 결과에 없습니다."
    else:
        logger.warning(f"{tc_id}: 조회된 데이터가 없습니다.")

#자동화코드 [2] ---------------------------------------
@pytest.mark.course
@pytest.mark.parametrize("data", data_all["detail_info"])
def test_get_detail_info(api_client_factory, data):
    """
    상세 정보 정합성 검증 (헬퍼 함수를 사용하여 가독성 향상)
    """
    logger.info(f"{data['tc_id']} 실행: {data['desc']}")

    client = api_client_factory(url_type=data['url_type'])
    # YAML에 있는 {ORG_NAME} 문자열을 실제 config 값으로 치환
    path = data['path'].format(ORG_NAME=ORG_NAME)

    response = client.get(path, params=data['params'])
    assert client.status_code == 200, f"[{data['tc_id']}] HTTP 에러: {client.status_code}"

    target_list = response.get(data['response_key'], []) if data['response_key'] else response
    if not isinstance(target_list, list):
        target_list = [target_list]

    found = _is_title_in_list(target_list, data['exp_title'])
    assert found, f"[{data['tc_id']}] 리스트 내에 '{data['exp_title']}' 항목이 없습니다."
    logger.info(f"{data['tc_id']} 성공 확인")

#자동화코드 [3] ---------------------------------------
@pytest.mark.course
def test_get_detail_unauthorized_body_check(api_client_factory):
    """
    SCH-18: 잘못된 토큰 시 응답 바디 내 403 에러 코드 검증
    """
    logger.info("SCH-18 실행")
    invalid_token = "Bearer_Invalid_Token_Example"
    client = api_client_factory(url_type="rest", custom_token=invalid_token)
    
    path = f"/org/{ORG_NAME}/course/lectureroom/get/"
    params = {"lectureroom_id": 135111}

    response = client.get(path, params=params)

    assert client.status_code == 200
    result = response.get("_result", {})
    assert result.get("status_code") == 403
    logger.info("SCH-18 성공")

#자동화코드 [4] ---------------------------------------
@pytest.mark.course
@pytest.mark.parametrize("data", data_all["boundary_cases"])
def test_get_schedule_boundary(api_client_factory, data):
    """
    SCH-19,20: 경계값테스트 : 서버가 400으로 막거나, 200(빈 리스트)을 줘야 함
    """
    tc_id = data['tc_id']
    logger.info(f"{tc_id} 실행: {data['desc']}")
    
    client = api_client_factory(url_type="classroom")
    params = {
        "classroom_id": CLASSROOM_ID,
        "dt_start_ge": data['start_ge'],
        "dt_start_le": data['start_le'],
        "count": 40
    }
    
    try:
        response = client.get("/schedule", params=params)
        assert client.status_code == 200
        assert isinstance(response, list) and len(response) == 0
        logger.info(f"{tc_id}: 200 OK 확인")
    except Exception as e:
        assert "400" in str(e)
        logger.info(f"{tc_id}: 400 에러 확인")

#자동화코드 [5] ---------------------------------------
@pytest.mark.course
def test_get_schedule_missing_org_header(api_client_factory):
    """
    SCH-21: 필수 커스텀 헤더 누락 시 409 에러 검증
    """
    logger.info("SCH-21 실행")
    client = api_client_factory(url_type="classroom")
    if "x-elice-org-name-short" in client.session.headers:
        del client.session.headers["x-elice-org-name-short"]

    
    params = {
        "classroom_id": CLASSROOM_ID, 
        "dt_start_ge": "2025-12-17T15:00:00.000Z", 
        "dt_start_le": "2026-02-14T14:59:59.999Z", 
        "count": 40
    }

    with pytest.raises(Exception) as excinfo:
        client.get("/schedule", params=params)
    
    
    assert "409" in str(excinfo.value)
    logger.info("SCH-21 성공")