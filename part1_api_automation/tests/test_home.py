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
    with pytest.raises(Exception) as e:
        client.get(f"/classroom/{CLASSROOM_ID}")

    assert "403" in str(e.value)
    assert "no_access_token"  in str(e.value)
#--------------------------------------------------------------------
# HOME_03[공통] 클래스홈 페이지 접속(토큰 만료)    
#--------------------------------------------------------------------   
def test_get_classhome_extoken():
    token = AuthManager.get_extoken()
    client = ApiClient(token=token, url_type="classroom")
    
    with pytest.raises(Exception) as e:
        client.get(f"/classroom/{CLASSROOM_ID}")
    
    assert "403" in str(e.value)
    assert "authorization failed" in str(e.value)
#--------------------------------------------------------------------
# HOME_04[공통] org 헤더 누락  -> 이거 원래 누락 되면 응답 안왔는데 왜 오늘은 오는거죠
#--------------------------------------------------------------------   

#--------------------------------------------------------------------
# HOME_05[이모지] 오늘의 기분 POST   
#--------------------------------------------------------------------   
# def test_post_emotion():
#     token = AuthManager.get_token()
#     client = ApiClient(token=token, url_type="classroom")
#     data = {"classroom_id": str(CLASSROOM_ID), "emoji": "good"}
    
#     try:
#         client.post("/emotion", data=data)
#     except Exception as e:
        