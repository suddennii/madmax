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
from utils.config import CLASSROOM_ID,ACCOUNT_ID,ACCOUNT_ID2,ORGANIZATION_ID,ELICE_COURSE_ID

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
# HOME_25[랜딩페이지] 랜딩페이지 get요청 organization_id누락
#--------------------------------------------------------------------
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
# HOME_26[랜딩페이지] 랜딩페이지 get요청 count누락
#--------------------------------------------------------------------