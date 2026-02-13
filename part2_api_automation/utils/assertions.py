"""
파일 목적 : 공통 Assertion 함수 모음

**작성자** : 박지우 / **작성일** : 26.02.09
**작성자** : 박지우 / **수정일** : 26.02.09

**테스트 목적 :**
- 테스트 코드에서 반복되는 검증 로직을 모듈화하여
가독성과 재사용성을 높이기 위한 파일.
- 중복 작성된 검증 내용을 함수로 관리한다.

기타 주의 사항 : 없음
"""

from utils.logger import logger
import pytest

# ---------------------------------------------------------
# API Error Assertion
# 예외 메시지에서 code/type이 기대값과 일치하는지 검증
# ---------------------------------------------------------
def assert_api_error(exc, expected):
    error = str(exc)
    if "code" in expected:
        assert str(expected["code"]) in error
    if "type" in expected:
        assert expected["type"] in error

# ---------------------------------------------------------
# Negative API Call Negative 
 # - 정상 응답이 오면 실패 처리
 # - 예외 발생 시 assert_api_error로 검증
# ---------------------------------------------------------
def assert_negative_api_call(client, endpoint, expected):
    try:
        response = client.get(endpoint)
        pytest.fail(
            f"예외가 발생해야 하는데 정상 응답 됨.\n"
            f"예상 응답 : {expected}\n"
            f"실제 응답 : {response}"
        )
    except Exception as exc:
        log_response(str(exc))
        assert_api_error(exc, expected)

# ---------------------------------------------------------
# Required Fields Assertion
# 응답 객체에 필수 필드가 모두 포함되어 있는지 확인
# ---------------------------------------------------------
def assert_required_fields(item, fields):
    for field in fields:
        assert field in item

# ---------------------------------------------------------
# Score Range Assertion
# 점수 필드(learning/test/practice)가 0~100 범위인지 검증
# ---------------------------------------------------------
def assert_score_range(item):
    learning = float(item["learning_progress"])
    test = float(item["test_score"])
    practice = float(item["practice_score"])
    assert 0 <= learning <= 100
    assert 0 <= test <= 100
    assert 0 <= practice <= 100

# ---------------------------------------------------------
# Response Logging
# ---------------------------------------------------------
def log_response(response):
    logger.info(f"실제 응답:{response}")
    if isinstance(response, dict) and "code" in response:
        logger.info(f"응답 코드: {response['code']}")


