"""
파일 목적 : 대쉬보드 API 테스트

**작성자** : 박지우 / **작성일** : 26.02.04
**작성자** : 박지우 / **수정일** : 26.02.09

**테스트 목적 :**
- 대시보드 API의 정상/에러 응답을 검증한다.
- 파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.
- 토큰 없이 API 호출이 불가한지 확인한다.
- A 토큰의 B 학생 데이터를 조회할 경우 API 호출이 불가한지 확인한다.

기타 주의 사항 : 없음
"""

import pytest
from utils.logger import logger
from utils.endpoints import build_student_course_endpoint
from utils.endpoints import build_student_account_endpoint
from utils.config import load_yaml
from utils.assertions import assert_required_fields, assert_score_range, assert_api_error,assert_negative_api_call
from utils.assertions import log_response

# ------------------------------------------------------------
# 1) course list (Positive)
# 과목 조회 및 과목 당 progress, score 정상 조회 확인
# DASH-T01 DASH-T02  DASH-T03  DASH-T05
# ------------------------------------------------------------
data = load_yaml("test_data/basic.yml")["params"]
@pytest.mark.parametrize("params", data)
def test_course_list(client_factory, token, params):
    client = client_factory(token, "dash")  
    endpoint = build_student_course_endpoint(params)
    response = client.get(endpoint)
    log_response(response)
    for item in response:
        assert_required_fields(item, ["course", "learning_progress", "test_score", "practice_score"])
        assert_score_range(item)
    if "expected" in params:
        assert len(response) == params["expected"]["items"]
        logger.info(response)
        logger.info(params["expected"]["items"])

# ------------------------------------------------------------
# 2) Course List - Missing Params (Negative)
# 필수 마라미터 누락 시 API 응답 확인
# DASH-T06
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["no_params"]
@pytest.mark.parametrize("params", data)
def test_no_param(client_factory, token, params):
    client = client_factory(token, "dash")
    endpoint = build_student_course_endpoint(params)
    assert_negative_api_call(client, endpoint, params["expected"])

# ------------------------------------------------------------
# 3) Course List - Wrong Params (Negative)
# 잘못된 파라미터 값 입력시 API 응답 값 확인
# DASH-T07 DASH-T08 DASH-T19 DASH-T20 DASH-T21 DASH-T22
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["wrong_params"]
@pytest.mark.parametrize("params", data)
def test_wrong_param(client_factory, token, params):
    client = client_factory(token, "dash")
    endpoint = build_student_course_endpoint(params)
    assert_negative_api_call(client, endpoint, params["expected"])

# ------------------------------------------------------------
# 4) No Token all (Negative)
# 인증 토큰이 없을 때 응답 거절 확인 (url) 
# DASH-T04 DASH-T11 DASH-T16
# -----------------------------------------------------------
DATA = load_yaml("test_data/basic.yml")
TEST_CASES = [
    ("dash", DATA["params"]),
    ("classroom", DATA["classroom_params"]),
    ("dash", DATA["account_no_token"]),
]
@pytest.mark.parametrize("url_type, params_list", TEST_CASES)
def test_no_token_all(client_factory, no_token, url_type, params_list):
    for params in params_list:
        client = client_factory(no_token, url_type)
        endpoint = build_student_course_endpoint(params)
        assert_negative_api_call(client, endpoint, {"code": 403, "type": "no_access_token"})

# ------------------------------------------------------------
# 5) Classroom List (Positive)
# 파라미터 설정에 따라 값이 정상 출력되는지 확인
# DASH-T09 DASH-T10 
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["classroom_params_positive"]
@pytest.mark.parametrize("params", data)
def test_dash_classroom_list(client_factory, token, params):
    client = client_factory(token, "classroom")
    endpoint = build_student_course_endpoint(params)
    response = client.get(endpoint)
    log_response(response)
    assert len(response) <= params["expected"]["items"]

# ------------------------------------------------------------
# 6) Classroom List (Negative)
# classroom id 값이 잘못 들어갔을 때 api 응답 테스트
# params1 에서 422가 떠야하는데 500이 뜸 (count 파라미터 음수)
# DASH-T12 DASH-T13
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["classroom_params_negative"]
@pytest.mark.parametrize("params", data)
def test_dash_classroom_list_negative(client_factory, token, params):
    client = client_factory(token, "classroom")
    endpoint = build_student_course_endpoint(params)
    assert_negative_api_call(client, endpoint, params["expected"])

# ------------------------------------------------------------
# 7) Account Info (Positive)
# 올바른 id의 정보가 조회 되는지 확인
# DASH-T14
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["account"]
@pytest.mark.parametrize("params", data)
def test_dash_account_list(client_factory, token, params):
    client = client_factory(token, "dash")
    endpoint = build_student_account_endpoint(params)
    response = client.get(endpoint)
    log_response(response)
    assert response["account"]["id"] == params["expected"]["id"]

# ------------------------------------------------------------
# 8) Account Info (Negative)
# 토큰 정보가 다른 account_id로 조회 거절되어야 하나 조회됨
# DASH-T15
# -----------------------------------------------------------
data = load_yaml("test_data/basic.yml")["account_negative"]
@pytest.mark.parametrize("params", data)
def test_dash_account_list_negative(client_factory, token, params):
    client = client_factory(token, "dash")
    endpoint = build_student_account_endpoint(params)
    assert_negative_api_call(client, endpoint, params["expected"])

