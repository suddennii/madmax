'''
파일 목적 : 
수업일정 API 기능 검증 코드
작성자 : 김건후 / 작성일 : 26.02.04
테스트 목적 : 
-수업일정 API의 정상 응답 및 데이터 정합성을 검증한다.
'''

import pytest
from utils.api_client import ApiClient
from utils.config import CLASSROOM_ID, ORG_NAME
from utils.logger import logger

# 테스트 데이터: (TC ID, 설명, 시작일, 종료일, 검증할_특정_날짜)
test_data = [
    ("SCH-01", "캘린더 페이지 최초 진입 시 금주 일정 조회", 
     "2026-01-17T15:00:00.000Z", "2026-03-14T14:59:59.999Z", "2026-02-02"),
    ("SCH-02", "리스트 보기 전환 시 일정 조회", 
     "2025-12-17T15:00:00.000Z", "2027-01-14T14:59:59.999Z", None),
    ("SCH-04", "지난 주(<) 일정 조회", 
     "2025-12-17T15:00:00.000Z", "2026-02-14T14:59:59.999Z", "2026-01-02"),
    ("SCH-07", "(>) 버튼 사용하여 다음 달 일정 조회",
     "2026-02-14T15:00:00.000Z","2026-04-14T14:59:59.999Z", None)
]

@pytest.mark.course
@pytest.mark.parametrize("tc_id, desc, start_ge, start_le, target_date", test_data)
def test_get_schedule_list(token, tc_id, desc, start_ge, start_le, target_date):
    """
    수업 일정 조회 기능 검증 (TC별 맞춤 날짜 검증 포함)
    """
    logger.info(f"▶ {tc_id} 실행: {desc}")

    # 1. 준비
    client = ApiClient(token=token, url_type="classroom")
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})

    params = {
        "classroom_id": CLASSROOM_ID,
        "dt_start_ge": start_ge,
        "dt_start_le": start_le,
        "count": 40,
    }

    # 2. 실행
    response = client.get("/schedule", params=params)

    # 3. 검증 (Assert)
    # [검증 1] 상태 코드 200 확인
    assert client.status_code == 200, f"[{tc_id}] 응답 코드 에러: {client.status_code}"
    
    # [검증 2] 응답 데이터가 리스트 형식인지 확인
    assert isinstance(response, list), f"[{tc_id}] 응답 데이터 형식 에러"
    
    if len(response) > 0:
        first_item = response[0]
        # [검증 3] 필수 필드 존재 확인 (id, dt_start)
        assert "id" in first_item and "dt_start" in first_item, f"[{tc_id}] 필수 필드 누락"
        
        # [검증 4] 데이터 정합성 (요청한 Classroom ID 일치 여부)
        if "tags" in first_item and "classroom_id" in first_item["tags"]:
            assert first_item["tags"]["classroom_id"] == CLASSROOM_ID, f"[{tc_id}] ID 불일치"

        # [검증 5] 특정 날짜 수업 데이터 존재 확인 (target_date가 설정된 경우만)
        if target_date:
            found_target = any(target_date in s.get("dt_start", "") for s in response)
            
            if found_target:
                logger.info(f"✅ {tc_id}: {target_date} 수업 데이터 확인됨")
            
            assert found_target, f"[{tc_id}] {target_date} 수업 데이터가 결과에 없습니다."
    else:
        logger.warning(f"⚠️ {tc_id}: 조회된 데이터가 없습니다.")


# 상세 조회 테스트 데이터: 각 API의 고유한 파라미터 구조를 반영
detail_test_data = [
    # 1. 강의실 상세 조회 (ApiClient의 url_type="rest" 사용)
    {
        "tc_id": "SCH-DETAIL-01",
        "desc": "3팀 회의실 상세 조회",
        "url_type": "rest",
        "path": f"/org/{ORG_NAME}/course/lectureroom/get/",
        "params": {"lectureroom_id": 135111},
        "response_key": "lectureroom",
        "exp_title": "3팀 회의실"
    },
    # 2. 프로젝트 오리엔테이션 상세 조회 (새로 가져오신 URL 기반)
    {
        "tc_id": "SCH-DETAIL-02",
        "desc": "프로젝트 오리엔테이션 상세 모달 열림",
        "url_type": "course", # api-course.elice.io 도메인 대응
        "path": "/lecture_page",
        "params": {
            "filter_lecture_id": 6657778,
            "filter_locator_type": 0,
            "filter_is_opened": "true",
            "skip": 0,
            "count": 10,
            "elice_course_id": 768550
        },
        "response_key": None, # 이 API는 최상위가 리스트 혹은 객체일 수 있음
        "exp_title": "02.02(월) 프로젝트 오리엔테이션"
    },
    # 3. QR 체크인 상세 조회
    {
        "tc_id": "SCH-DETAIL-03",
        "desc": "QR 체크인/체크아웃 상세 조회",
        "url_type": "rest",
        "path": f"/org/{ORG_NAME}/course/get/",
        "params": {"course_id": 759075},
        "response_key": "course",
        "exp_title": "QR 체크인/체크아웃"
    }
]

@pytest.mark.course
@pytest.mark.parametrize("data", detail_test_data)
def test_get_detail_info(token, data):
    """
    상세 정보 정합성 검증 (중첩된 lecture 객체 내 제목까지 전수 조사)
    """
    logger.info(f"▶ {data['tc_id']} 실행: {data['desc']}")

    client = ApiClient(token=token, url_type=data['url_type'])
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})

    response = client.get(data['path'], params=data['params'])

    assert client.status_code == 200, f"[{data['tc_id']}] HTTP 에러: {client.status_code}"

    # 1. 대상 리스트 추출
    target_list = response.get(data['response_key'], []) if data['response_key'] else response
    if not isinstance(target_list, list):
        target_list = [target_list]

    # 2. 전수 조사 (중첩된 lecture 내 title까지 확인)
    found = False
    for item in target_list:
        # (1) 겉에 있는 title 확인
        top_title = item.get("title", "")
        # (2) lecture 객체 내부에 있는 title 확인
        lecture_title = item.get("lecture", {}).get("title", "") if item.get("lecture") else ""
        
        # 둘 중 하나라도 기대하는 제목을 포함하고 있으면 통과!
        if data['exp_title'] in top_title or data['exp_title'] in lecture_title:
            found = True
            break

    assert found, f"[{data['tc_id']}] 리스트 내(겉/내부)에 '{data['exp_title']}'을 포함한 항목이 없습니다."
    
    logger.info(f"✅ {data['tc_id']} 성공: '{data['exp_title']}' 항목을 확인했습니다.")


@pytest.mark.course
def test_get_detail_unauthorized_body_check(token):
    """
    SCH-ERROR-01: 잘못된 토큰 시 응답 바디 내 403 에러 코드 검증
    """
    logger.info("▶ SCH-ERROR-01 실행: 응답 바디 내 403(auth) 차단 확인")

    # 1. 준비: 위조된 토큰 설정
    invalid_token = "Bearer_Invalid_Token_Example"
    client = ApiClient(token=invalid_token, url_type="rest")
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})
    
    path = f"/org/{ORG_NAME}/course/lectureroom/get/"
    params = {"lectureroom_id": 135111}

    # 2. 실행: 이제 Exception이 발생하지 않으므로 바로 response를 받습니다.
    response = client.get(path, params=params)

    # 3. 검증 (포스트맨 응답 구조 기준)
    # [검증 1] HTTP 상태 코드는 200 OK 여야 함 (서버 규격)
    assert client.status_code == 200, f"HTTP 상태 코드 에러: {client.status_code}"

    # [검증 2] _result 내 status_code가 403인지 확인
    result = response.get("_result", {})
    assert result.get("status_code") == 403, f"기대 수치(403)와 다름: {result.get('status_code')}"
    
    # [검증 3] 실패 사유 및 메시지 확인
    assert result.get("status") == "fail", "응답 상태가 'fail'이 아님"
    assert "authorization failed" in response.get("fail_message", ""), "에러 메시지 문구 불일치"

    logger.info(f"✅ SCH-ERROR-01 성공: 바디 내 403 코드 및 'authorization failed' 확인 완료")


# [신규 추가] 경계값 테스트 데이터
boundary_data = [
    ("SCH-10", "과거 날짜(1900년)", "1900-01-17T15:32:08.000Z", "1900-03-14T15:32:07.999Z"),
    ("SCH-11", "미래 날짜(2099년)", "2099-01-17T15:00:00.000Z", "2099-03-14T14:59:59.999Z")
]

@pytest.mark.course
@pytest.mark.parametrize("tc_id, desc, start_ge, start_le", boundary_data)
def test_get_schedule_boundary(token, tc_id, desc, start_ge, start_le):
    """
    경계값 테스트: 서버가 400으로 막거나, 200(빈 리스트)을 줘야 함
    """
    logger.info(f"▶ {tc_id} 실행: {desc}")
    
    # 1. 준비
    client = ApiClient(token=token, url_type="classroom")
    client.session.headers.update({"x-elice-org-name-short": ORG_NAME})

    params = {
        "classroom_id": CLASSROOM_ID,
        "dt_start_ge": start_ge,
        "dt_start_le": start_le,
        "count": 40
    }
    
    # 2. 실행 및 검증
    # ApiClient 특성상 400 에러 시 Exception이 발생할 수 있으므로 try-except로 처리
    try:
        response = client.get("/schedule", params=params)
        
        # Case A: 200 OK가 왔다면? 데이터가 비어있어야 함 (미래/과거니까)
        assert client.status_code == 200, f"[{tc_id}] 상태 코드 에러: {client.status_code}"
        assert isinstance(response, list) and len(response) == 0, \
            f"[{tc_id}] 데이터가 없어야 하는데 {len(response)}건이 조회됨"
            
        logger.info(f"✅ {tc_id}: 200 OK와 함께 빈 데이터([]) 확인됨")
        
    except Exception as e:
        # Case B: 에러가 났다면? 그 에러가 400(Bad Request)이어야 함
        # 에러 메시지에 '400'이라는 숫자가 포함되어 있는지 확인
        assert "400" in str(e), f"[{tc_id}] 400 에러를 기대했으나 다른 에러 발생: {e}"
        logger.info(f"✅ {tc_id}: 서버가 400 에러로 정상 차단함")


@pytest.mark.course
def test_get_schedule_missing_org_header(token):
    """
    SCH-ERROR-02: 필수 커스텀 헤더(x-elice-org-name-short) 누락 시 409 에러 검증
    """
    logger.info("▶ SCH-ERROR-02 실행: 조직명 헤더 누락 시 409 Conflict 확인")

    # 1. 준비: 토큰은 정상적으로 넣되, 조직명 헤더를 추가하지 않은 클라이언트를 생성합니다.
    client = ApiClient(token=token, url_type="classroom")
    # ⚠️ 중요: 아래 헤더 업데이트를 수행하지 않거나, 명시적으로 삭제합니다.
    if "x-elice-org-name-short" in client.session.headers:
        del client.session.headers["x-elice-org-name-short"]

    # 스크린샷에 명시된 파라미터
    params = {
        "classroom_id": "a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc",
        "dt_start_ge": "2025-12-17T15:00:00.000Z",
        "dt_start_le": "2026-02-14T14:59:59.999Z",
        "count": 40
    }

    # 2. 실행 및 예외 포착 (409 에러는 Exception을 발생시킵니다)
    with pytest.raises(Exception) as excinfo:
        client.get("/schedule", params=params)

    # 3. 검증 (스크린샷 결과 기반)
    error_msg = str(excinfo.value)
    
    # [검증 1] 응답 코드가 정확히 409인지 확인
    assert "409" in error_msg, f"409 Conflict 에러가 발생해야 함: {error_msg}"

    # [검증 2] 에러 메시지에 'Failed to connect' 또는 'NoneType' 관련 내용이 있는지 확인
    # 스크린샷의 error_message 필드 내용을 참고했습니다.
    assert "Failed to connect" in error_msg or "NoneType" in error_msg, \
        f"기대하는 에러 상세 메시지가 아님: {error_msg}"

    logger.info(f"✅ SCH-ERROR-02 성공: 서버가 409 Conflict로 필수 헤더 누락을 정상 차단함")