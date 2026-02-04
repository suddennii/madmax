import pytest
from utils.endpoints import student_course
from utils.api_client import ApiClient

# TEST_ENDPOINT = "/student/{account_id}/course?classroom_id={classroom_id}&offset={offset}&count={count}"

def test_course_list(client, student_course_parmas):
    client = ApiClient(url_type="dash")
    for params in student_course_parmas:
        endpoint = student_course(
            account_id=params["account_id"],
            classroom_id=params["classroom_id"],
            offset=params["offset"],
            count=params["count"]
        )
        response = client.get(endpoint)
        assert response.status_code==200
    