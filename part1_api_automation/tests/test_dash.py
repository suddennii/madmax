import pytest
from utils.endpoints import student_course
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.logger import logger
from utils.config import basic_json
from utils.config import build_student_course_endpoint
from utils.config import load_yaml


data = load_yaml("test_data/basic.yml")

# DASH-T01, DASH-T02, DASH-T03, DASH-T05
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

# no_token test
@pytest.mark.parametrize("params", basic_json()["params"])
def test_no_token(client, params):
    client = ApiClient(token=None, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)
    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    assert "403" in str(exc.value)
    assert "no_access_token" in str(exc.value)

# no_param test
@pytest.mark.parametrize("params", basic_json()["no_params"])
def test_no_param(client, params):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    endpoint = build_student_course_endpoint(params)
    with pytest.raises(Exception) as exc:
        client.get(endpoint)
    assert "422" in str(exc.value)
    assert "missing" in str(exc.value)
    assert "Field required" in str(exc.value)
    logger.info(str(exc.value))

