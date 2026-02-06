'''
파일 목적 :
- 클래스 홈테스트 수행 코드

작성자 : 신윤아 / 작성일 : 26.02.04

테스트 목적 :
-클래스홈 API의 정상/에러 응답을 검증한다.
-파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.


기타 주의 사항 :
- test_post_emotion() 은 하루 한번만 pass되는것이 정상, 이후 409에러 반환

'''
import os 
import pytest
from datetime import datetime
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.config import CLASSROOM_ID,ACCOUNT_ID
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
@pytest.mark.xfail(reason="하루 1회 제한으로 인한 중복 에러 허용")
def test_post_emotion():
    token = AuthManager.get_token()
    client = ApiClient(token=token, url_type="classroom")
    data = {"classroom_id": str(CLASSROOM_ID), "emoji": "good"}
    try:
        res = client.post("/emotion", data=data)
        assert res.status_code ==200
    except Exception as e:
        if "unique_constraint_violation" in str(e):
            pytest.xfail("이미 오늘 감정 표현을 완료함.")
        raise e
 
#--------------------------------------------------------------------
# HOME_06[이모지] 오늘의 기분 PATCH  
#--------------------------------------------------------------------   
def test_patch_emotion():
    today_date = datetime.now().strftime("%Y-%m-%d")
    token = AuthManager.get_token()
    client = ApiClient(token=token, url_type="classroom")
    
    params = {"classroom_id": CLASSROOM_ID, "filter_record_date": today_date}
    data = {"classroom_id": str(CLASSROOM_ID), "emoji": "bad"}
    
    #내 감정 기록 조회 (GET)
    get_res = client.get(f"/emotion", params=params)
    my_record = next((item for item in get_res if item.get("account_id") == ACCOUNT_ID), None)
    
    #내 기록에서 동적id가져오기
    if my_record:
        dynamic_id = my_record.get("id") 
    else:
        pytest.fail(f"해당 날짜({today_date})에 내 감정 기록이 없습니다. 먼저 POST를 해주세요!")
    #patch날리기
    try:
        client.patch(f"/emotion/{dynamic_id}", data=data)
    except Exception as e:
        pytest.fail(f"PATCH 요청 중 에러 발생: {e}")

#--------------------------------------------------------------------
# HOME_07[이모지] 오늘의 기분 get
#--------------------------------------------------------------------   
def test_get_emotion():
    today_date = datetime.now().strftime("%Y-%m-%d")
    token = AuthManager.get_token()
    client = ApiClient(token=token, url_type="classroom")
    params = {"classroom_id": CLASSROOM_ID, "filter_record_date": today_date}
    
    res = client.get(f"/emotion", params=params)
    
    assert res[0]["emoji"] in ("good", "neutral", "bad"),"오늘의 감정 기록이 없습니다."
    
#--------------------------------------------------------------------
# HOME_08[이모지] 필수 param입력 누락
#-------------------------------------------------------------------- 
def test_get_emotion_noclassid():
    token = AuthManager.get_token()
    client = ApiClient(token=token, url_type="classroom")
    
    with pytest.raises(Exception) as e:
        client.get(f"/emotion")
    assert "422" in str(e.value)
    
#--------------------------------------------------------------------
# HOME_09[이어서 학습] get요청
#-------------------------------------------------------------------- 
# def test_get_study():
#     token = AuthManager.get_token()
#     client = ApiClient(token=token)