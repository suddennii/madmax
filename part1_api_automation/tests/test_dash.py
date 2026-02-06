import pytest
from utils.endpoints import student_course
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.logger import logger
from utils.config import build_student_course_endpoint
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

    