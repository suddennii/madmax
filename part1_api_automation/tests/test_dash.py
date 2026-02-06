"""
파일 목적 : 대쉬보드 API 테스트

**작성자** : 박지우 / **작성일** : 26.02.04
**작성자** : 조대건 / **수정일** : 26.02.06

**테스트 목적 :**
- 대시보드 API의 정상/에러 응답을 검증한다.
- 파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.
- 토큰 없이 API 호출이 불가한지 확인한다.
- A 토큰의 B 학생 데이터를 조회할 경우 API 호출이 불가한지 확인한다.

기타 주의 사항 : 없음
"""

import pytest
from utils.endpoints import student_course
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.logger import logger
from utils.config import build_student_course_endpoint
from utils.config import build_student_account_endpoint
from utils.config import load_yaml

data = load_yaml("test_data/basic.yml")["params"]
# 정상통과와 리스크 갯수 반환
@pytest.mark.parametrize("params", data)
def test_course_list(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)
    response = client.get(endpoint)
    logger.info(f"RAW RESPONSE: {response}")
    logger.info(f"TYPE: {type(response)}")

    # 공통 검증
    for item in response:
        assert "course" in item
        assert "learning_progress" in item
        assert "test_score" in item
        assert "practice_score" in item
        learning = float(item["learning_progress"])
        test = float(item["test_score"])
        practice = float(item["practice_score"])
        assert 0 <= learning <= 100
        assert 0 <= test <= 100
        assert 0 <= practice <= 100

    if "expected" in params:
        assert len(response) == params["expected"]["items"]
        logger.info(response)
        logger.info(params["expected"]["items"])

# no_param test (파라미터가 없는 경우)
data = load_yaml("test_data/basic.yml")["no_params"]
@pytest.mark.parametrize("params", data)
def test_no_param(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)

    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    assert "422" in str(exc.value)
    assert "missing" in str(exc.value)
    assert "Field required" in str(exc.value)

# 정상 파라미터가 아닌경우 wrong_params
data = load_yaml("test_data/basic.yml")["wrong_params"]
@pytest.mark.parametrize("params", data)
def test_wrong_param(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)

    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    error = str(exc.value)
    assert str(params["expected"]["code"]) in error
    assert params["expected"]["type"] in error


# no_token test
@pytest.mark.parametrize("params", data)
def test_no_token(client, params):
    client = ApiClient(token=None, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)
    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    assert "403" in str(exc.value)
    assert "no_access_token" in str(exc.value)


# base_url classroom 테스트 classroom_param_positive
data = load_yaml("test_data/basic.yml")["classroom_params_positive"]
@pytest.mark.parametrize("params", data)
def test_dash_classroom_list(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="classroom") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)
    
    response = client.get(endpoint)
    logger.info(f"RAW RESPONSE: {response}")
    logger.info(f"TYPE: {type(response)}")

    response = client.get(endpoint)
    assert len(response) <= params["expected"]["items"]

# base_url classroom 테스트 classroom_param_negetive
data = load_yaml("test_data/basic.yml")["classroom_params_negative"]
@pytest.mark.parametrize("params", data)
def test_dash_classroom_list_negative(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="classroom") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)

    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    error = str(exc.value)
    assert str(params["expected"]["code"]) in error
    assert params["expected"]["type"] in error

# base_url account 테스트 
data = load_yaml("test_data/basic.yml")["account"]
@pytest.mark.parametrize("params", data)
def test_dash_account_list(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_account_endpoint(params)
    
    response = client.get(endpoint)
    logger.info(f"RAW RESPONSE: {response}")
    logger.info(f"TYPE: {type(response)}")

    response = client.get(endpoint)
    assert response["account"]["id"] == params["expected"]["id"]

# 다른 account_id로 조회 거절 확인
data = load_yaml("test_data/basic.yml")["account_negative"]
@pytest.mark.parametrize("params", data)
def test_dash_account_list_negative(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_account_endpoint(params)

    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    error = str(exc.value)
    assert str(params["expected"]["code"]) in error
    assert params["expected"]["type"] in error

