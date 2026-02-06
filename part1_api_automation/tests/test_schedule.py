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