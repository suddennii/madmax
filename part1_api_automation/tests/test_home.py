'''
작성자 : 신윤아
클래스 홈 api test
'''
import os 
import pytest
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.config import CLASSROOM_ID
#--------------------------------------------------------------------
# HOME_01[공통] 클래스홈 페이지 접속    
#--------------------------------------------------------------------
def test_get_classhome_status():
    token = AuthManager.get_token()
    client = ApiClient(token=token, url_type="classroom")
    res = client.get(
        f"/classroom/{CLASSROOM_ID}"
    )
    # assert res["code"] == 200 <- 코드를 반환하지 않음..
    assert res["id"]  == CLASSROOM_ID
#--------------------------------------------------------------------
# HOME_02[공통] 클래스홈 페이지 접속(토큰 누락)    
#--------------------------------------------------------------------   
def test_get_classhome_notoken():
    client = ApiClient(token=None, url_type="classroom") 
    res = client.session.get(
        client.base_url + f"/classroom/{CLASSROOM_ID}"
        )

    assert res.status_code == 403
    assert res.json()["code"] == "no_access_token"
#--------------------------------------------------------------------
# HOME_03[공통] 클래스홈 페이지 접속(토큰 만료)    
#--------------------------------------------------------------------   
# def test_get_classhome_extoken():
#     token = AuthManager.get_extoken()
#     client = ApiClient(token=token, url_type="classroom")
#     res = client.get(
#         f"/classroom/{CLASSROOM_ID}"
#     )
    
    