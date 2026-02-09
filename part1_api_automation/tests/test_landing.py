'''
파일 목적 :
- 랜딩 페이지 테스트 수행 코드

작성자 : 신윤아 / 작성일 : 26.02.09

테스트 목적 :
-랜딩페이지 API의 정상/에러 응답을 검증한다.
-파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.

'''
import pytest
import json
from datetime import datetime,timezone
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.datetime_helper import select_time
from utils.config import CLASSROOM_ID,ACCOUNT_ID,CLASSROOM_ID2,ORGANIZATION_ID,ELICE_COURSE_ID

#--------------------------------------------------------------------
# HOME_23[랜딩페이지] 랜딩페이지 get요청
#--------------------------------------------------------------------
def test_landing_get():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="rest")
    params = {
        "organization_id":ORGANIZATION_ID,
        "offset" : 0,
        "count" : 10
    }
    
    res = client.get(f"/global/organization/landing/banner/list/",params=params)
    
    assert res["_result"]["status_code"] == 200

#--------------------------------------------------------------------
# HOME_24[랜딩페이지] 랜딩페이지 get요청 organization_id누락
#--------------------------------------------------------------------
def test_landing_get_noid():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="rest")
    params = {
        "offset" : 0,
        "count" : 10
    }
    res = client.get(f"/global/organization/landing/banner/list/",params=params)
    assert res["_result"]["status_code"] >= 400
    assert res["fail_code"] == "invalid_parameter"
    
#--------------------------------------------------------------------
# HOME_25[랜딩페이지] 랜딩페이지 get요청 offset누락
#--------------------------------------------------------------------
def test_landing_get_nooffset():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="rest")
    params = {
        "organization_id":ORGANIZATION_ID,
        "count" : 10
    }

    res = client.get(f"/global/organization/landing/banner/list/",params=params)

    assert res["_result"]["status_code"] >= 400
    assert res["fail_code"] == "invalid_parameter"

#--------------------------------------------------------------------
# HOME_26[랜딩페이지] 랜딩페이지 get요청 count누락
#--------------------------------------------------------------------
def test_landing_get_nocount():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="rest")
    params = {
        "organization_id":ORGANIZATION_ID,
        "offset" : 0,

    }
    
    res = client.get(f"/global/organization/landing/banner/list/",params=params)
    
    assert res["_result"]["status_code"] >= 400
    assert res["fail_code"] == "invalid_parameter"

#--------------------------------------------------------------------
# HOME_27[랜딩페이지] 랜딩페이지 공지사항 get요청
#--------------------------------------------------------------------
def test_landing_get_announcement():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="rest")
    params = {
        "organization_id":ORGANIZATION_ID,
        "offset" : 0,
        "count" : 10
    }
    res = client.get(f"/global/organization/notice/list/",params=params)
    assert res["_result"]["status_code"]==200
 
#--------------------------------------------------------------------
# HOME_28[랜딩페이지] 2기 클래스홈 get요청 시도
#--------------------------------------------------------------------
def test_2nd_classhome_get():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="classroom")
    with pytest.raises(Exception) as e:
        client.get(f"/classroom/{CLASSROOM_ID2}")
    assert "has_no_permission" in str(e.value)
    
 
#--------------------------------------------------------------------
# HOME_29[랜딩페이지] 전체강의 리스트 get요청
#--------------------------------------------------------------------
def test_course_list_get():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="rest")
    params = {
        "offset" : 0,
        "count" : 12
    }
    res =client.get(f"/org/qatrack/course/list/",params=params)
    assert res["_result"]["status_code"] == 200
    
 
#--------------------------------------------------------------------
# HOME_30[랜딩페이지] 내클래스 get요청
#--------------------------------------------------------------------
def test_get_myclass():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    params = {
        "skip" : 0,
        "count" : 10
    }
    res =client.get(f"/classroom",params=params)
    
    assert res[0]["id"] == CLASSROOM_ID, f"CLASSROOM_ID {CLASSROOM_ID}가 응답에 없습니다."
    