import pytest
from utils.endpoints import student_course
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager

def test_course_list(client, student_course_parmas):
    token = AuthManager.get_token() # 토큰 가져오고
    client = ApiClient(token=token, url_type="dash") # 이렇게 base url 불러올 수 있게
    for params in student_course_parmas:
        endpoint = student_course(
            account_id=params["account_id"],
            classroom_id=params["classroom_id"],
            offset=params["offset"],
            count=params["count"]
        )
        response = client.get(endpoint)
        for item in response:
            assert isinstance(item, dict)
            assert "course" in item
            assert "learning_progress" in item
            learning = float(item["learning_progress"])
            test = float(item["test_score"])
            practice = float(item["practice_score"])
            print(learning)
            print(test)
            print(practice)
            assert 0 <= learning <= 100
            assert 0 <= test <= 100
            assert 0 <= practice <= 100
