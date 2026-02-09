'''
파일 목적 :
- 클래스 홈테스트 수행 코드

작성자 : 신윤아 / 작성일 : 26.02.04
작성자 : 신윤아 / 수정일 : 26.02.09

테스트 목적 :
-클래스홈 API의 정상/에러 응답을 검증한다.
-파라미터 조합별 응답 코드가 기대값과 일치하는지 확인한다.


기타 주의 사항 :
- test_post_emotion() 은 하루 한번만 pass되는것이 정상, 이후 409에러 반환

'''
import os 
import pytest
import json
from datetime import datetime,timezone
from utils.api_client import ApiClient
from utils.auth_manager import AuthManager
from utils.datetime_helper import select_time
from utils.config import CLASSROOM_ID,ACCOUNT_ID,ACCOUNT_ID2,SANDBOX_COURSE_ID,ELICE_COURSE_ID
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
def test_get_study():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="dash")
    res =client.get(f"/classroom/{CLASSROOM_ID}/next_lecture_page")

    expected_fields = {
        "course_id"  : int,
        "lecture_id" : int,
        "lecture_page_id" : int,
        "course_title" : str,
        "lecture_page_title" : str
    }

    for field,data_type in expected_fields.items():
        assert field in res,f"응답에 {field}가 없습니다."
        assert isinstance(res[field],data_type),f"{field}필드는 {data_type.__name__}타입이여야 합니다."
        
#--------------------------------------------------------------------
# HOME_10[학습진행률] get요청
#-------------------------------------------------------------------- 
def test_get_progress():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="dash")
    params = {"classroom_id":CLASSROOM_ID}
    res = client.get(f"/student/{ACCOUNT_ID}", params=params)
    
    expected_fields = {
        "learning_progress"  : str,
        "test_score" : str,
        "practice_score" : str,
        "submit_cnt" : int,
        "test_completed_cnt" : int
    }
    for field,data_type in expected_fields.items():
        assert field in res,f"응답에 {field}가 없습니다."
        assert isinstance(res[field],data_type),f"{field}필드는 {data_type}타입이여야 합니다."
    
#--------------------------------------------------------------------
# HOME_11[학습진행률] get요청(다른사람account_id2)
#-------------------------------------------------------------------- 
#fail이 떠야 정상... 왜냐면 개인정보를 볼 수 있으니까요
def test_get_progress2():
    token = AuthManager.get_token()
    client = ApiClient(token=token,url_type="dash")
    params = {"classroom_id":CLASSROOM_ID}
    with pytest.raises(Exception) as e:
        res = client.get(f"/student/{ACCOUNT_ID2}", params=params)
        
    expected_fields = {
        "learning_progress"  : str,
        "test_score" : str,
        "practice_score" : str,
        "submit_cnt" : int,
        "test_completed_cnt" : int
    }
    for field,data_type in expected_fields.items():
        assert field in res,f"응답에 {field}가 없습니다."
        assert isinstance(res[field],data_type),f"{field}필드는 {data_type}타입이여야 합니다."

#--------------------------------------------------------------------
# HOME_12[오늘의 일정] 날짜이동 테스트
#-------------------------------------------------------------------- 
def test_get_todo():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(2026, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "classroom_id":CLASSROOM_ID,
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base,offset_days=1) }
       
    res = client.get(f"/schedule/count",params=params)
    
    
    assert "count" in res
    assert isinstance(res["count"],int)
    assert res["count"] >= 0
   
#--------------------------------------------------------------------
# HOME_13[오늘의 일정] 일정목록 get요청
#-------------------------------------------------------------------- 
def test_get_todolist():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(2026, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "classroom_id":CLASSROOM_ID,
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base,offset_days=1),
        "count" : 20}
    res = client.get(f"/schedule/ics",params=params)
    
    #JSON을 반환하지않고 .ics를 반환
    assert isinstance(res, str)
    assert "BEGIN:VCALENDAR" in res
    assert "SUMMARY" in res
    assert "END:VCALENDAR" in res
    
#--------------------------------------------------------------------
# HOME_14[오늘의 일정] 필수 param제거(class_id)
#-------------------------------------------------------------------- 
def test_get_todolist_no_classid():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(2026, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base,offset_days=1),
        "count" : 20}
    
    with pytest.raises(Exception) as e:
        client.get(f"/schedule/ics",params=params)
    assert "422" in str(e.value)
    
#--------------------------------------------------------------------
# HOME_15[오늘의 일정] 유효하지 않은 날짜 검증
#-------------------------------------------------------------------- 
def test_get_past_date():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(202, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base,offset_days=1),
        "count" : 20}
    
    with pytest.raises(Exception) as e:
        client.get(f"/schedule/ics",params=params)
    assert "422" in str(e.value)
    
#--------------------------------------------------------------------
# HOME_16[오늘의 일정] 동일한 날짜 입력
#-------------------------------------------------------------------- 
def test_same_date():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(2026, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "classroom_id":CLASSROOM_ID,
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base),
        "count" : 20}
    res = client.get(f"/schedule/ics",params=params)
    
    #JSON을 반환하지않고 .ics를 반환
    #동일한 시간 입력시 summary는 존재 X
    assert isinstance(res, str)
    assert "BEGIN:VCALENDAR" in res
    assert "SUMMARY" not in res
    assert "END:VCALENDAR" in res
    
#--------------------------------------------------------------------
# HOME_17[오늘의 일정] 동일한 날짜 입력
#-------------------------------------------------------------------- 
def test_more_date_ge():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    client.session.headers.update({"X-Elice-Org-Name-Short": "qatrack"})
    base = datetime(2026, 2, 9, 0, 0, tzinfo=timezone.utc)
    params = {
        "classroom_id":CLASSROOM_ID,
        "dt_start_ge": select_time(base_dt=base),
        "dt_start_le": select_time(base_dt=base,offset_days=-1),
        "count" : 20}
    
    with pytest.raises(Exception) as e:
        client.get(f"/schedule/ics",params=params)
    assert "409" in str(e.value)
    assert "invalid_datetime_format" in str(e.value)
    
#--------------------------------------------------------------------
# HOME_18[학습현황] 과목 페이징 get요청
#--------------------------------------------------------------------
def test_get_sublist():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="dash")
    params = {
        "classroom_id":CLASSROOM_ID,
        "offset" : 5,
        "count": 5
    }
    res = client.get(f"/student/{ACCOUNT_ID}/course",params=params)
    
    assert isinstance(res, list), "응답은 list여야 합니다."
    assert len(res) == params["count"], (
        f"응답 개수는 {params['count']}개여야 합니다."
    )

    expected_fields = {
        "course": dict,
        "learning_progress": str,
        "test_score": str,
        "practice_score": str,
        "submit_cnt": int,
        "test_completed_cnt": int,
    }
    course_fields = {
        "id": int,
        "title": str,
        "course_type": int,
        "logo_url": (str, type(None)),
    }

    for idx, item in enumerate(res):
        assert isinstance(item, dict), f"{idx}번째 요소는 dict여야 합니다."

        for field, data_type in expected_fields.items():
            assert field in item, f"{idx}번째 요소에 {field}가 없습니다."
            assert isinstance(item[field], data_type), (
                f"{idx}번째 요소의 {field}는 {data_type} 타입이어야 합니다."
            )

        #course내부 검증
        course = item["course"]
        for field, data_type in course_fields.items():
            assert field in course, f"{idx}번째 course에 {field}가 없습니다."
            assert isinstance(course[field], data_type), (
                f"{idx}번째 course의 {field}는 {data_type} 타입이어야 합니다."
            )

#--------------------------------------------------------------------
# HOME_20[학습현황] 세부과목 페이지 불러오기
#--------------------------------------------------------------------
def test_detail_sub_get():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    res = client.get(f"/classroom/{CLASSROOM_ID}/course/{SANDBOX_COURSE_ID}")
    
    assert res["title"] == "SANDBOX"
    
#--------------------------------------------------------------------
# HOME_21[학습현황] 다른 account_id로 get요청 시도
#--------------------------------------------------------------------
def test_account2_get_sub():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="rest")
    params = {
        "course_id":ELICE_COURSE_ID,
        "user_id" : ACCOUNT_ID2
    }
    
    res = client.get(f"/org/qatrack/dashboard/user/lecture_page/list/",params=params)
    
    assert res["_result"]["status_code"] == 409
    assert res["fail_code"] == "insufficient_permission"
    
#--------------------------------------------------------------------
# HOME_22[info] 수강생계정으로 로그인시 get요청 실패
#--------------------------------------------------------------------
def test_login_student_account_failget():
    token = AuthManager.get_token()
    client = ApiClient(token = token,url_type="classroom")
    with pytest.raises(Exception) as e:
        client.get(f"/classroom/{CLASSROOM_ID}/classroom_ticket/info")
    assert "has_no_permission" in str(e.value)

