import pytest
import time
from utils.api_client import ApiClient
from utils.config import CLASSROOM_ID
from utils.logger import logger

@pytest.mark.course
def test_get_schedule_list(token):
    """
    [TC-01] 캘린더 페이지 최초 진입 시 금주 일정 조회
    - 필수값(id, dt_start 등) 검증
    - 데이터 정합성(Classroom ID) 검증
    - 특정 날짜(2월 2일) 수업 존재 여부 확인
    - 응답 시간 1000ms(1초) 이하 검증
    """
    
    # 1. 준비 (Arrange)
    client = ApiClient(token=token, url_type="classroom")
    
    # [핵심] 포스트맨 헤더 추가
    client.session.headers.update({"x-elice-org-name-short": "qatrack"})

    params = {
        "classroom_id": CLASSROOM_ID,
        "dt_start_ge": "2026-01-17T15:00:00.000Z",
        "dt_start_le": "2026-03-14T14:59:59.999Z",
        "count": 40,
    }

    # 2. 실행 (Act) 및 시간 측정
    logger.info(f"스케줄 조회 시도: params={params}")
    
    start_time = time.time()  # 타이머 시작
    response = client.get("/schedule", params=params)
    end_time = time.time()    # 타이머 종료
    
    # 밀리초(ms) 단위로 변환 (1초 = 1000ms)
    duration_ms = (end_time - start_time) * 1000
    logger.info(f"응답 소요 시간: {duration_ms:.2f}ms")

    # 3. 검증 (Assert)
    
    # [검증 1] 응답 시간 1000ms 이하
    assert duration_ms <= 1000, f"응답 시간이 기준(1000ms)을 초과했습니다: {duration_ms:.2f}ms"

    # [검증 2] 상태 코드 200 (ApiClient 내부에서 400 이상이면 에러를 뱉음) 및 리스트 타입
    assert client.status_code == 200
    assert isinstance(response, list), "응답 데이터가 리스트 형식이 아닙니다."
    
    # 데이터가 있어야 상세 검증 가능
    if len(response) > 0:
        first_item = response[0]

        # [검증 3] 필수값 존재 여부 (Structure)
        assert "id" in first_item, "필수 필드 'id'가 누락되었습니다."
        assert "dt_start" in first_item, "필수 필드 'dt_start'가 누락되었습니다."
        assert "dt_end" in first_item, "필수 필드 'dt_end'가 누락되었습니다."
        
        # [검증 4] 데이터 정합성 (Data Integrity)
        # 요청한 Classroom ID의 데이터가 맞는지 확인
        if "tags" in first_item and "classroom_id" in first_item["tags"]:
            res_class_id = first_item["tags"]["classroom_id"]
            assert res_class_id == CLASSROOM_ID, f"요청한 ID({CLASSROOM_ID})와 응답 ID({res_class_id})가 불일치합니다."

        # [검증 5] 특정 날짜(2월 2일) 수업 존재 확인 (Target Date Validation)
        target_date_str = "2026-02-02"
        found_target_date = False
        
        for item in response:
            # dt_start 문자열 안에 "2026-02-02"가 포함되어 있는지 확인
            if target_date_str in item.get("dt_start", ""):
                found_target_date = True
                logger.info(f"{target_date_str} 수업 데이터 확인됨: {item.get('summary')}")
                break
        
        assert found_target_date, f"조회된 리스트 중 {target_date_str}에 시작하는 수업이 없습니다."

    else:
        logger.warning("조회된 스케줄 데이터가 없습니다. (날짜 범위나 데이터를 확인하세요)")