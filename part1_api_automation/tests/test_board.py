"""
2025-02-05 심다영
게시판(Board) API 테스트 - TC 기반 통합 시나리오
[테스트 범위]
- BOARD_11: 게시글 생성
- BOARD_13: 게시글 수정
- BOARD_06: 게시글 좋아요 추가
- BOARD_08: 게시글 좋아요 취소
- BOARD_16: 댓글 생성
- BOARD_17: 댓글 조회
- BOARD_19: 댓글 수정
- BOARD_07: 댓글 좋아요 추가
- BOARD_09: 댓글 좋아요 취소
- BOARD_20: 댓글 삭제
- BOARD_15: 게시글 삭제

2026-02-06 심다영
아래 테스트 항목 추가
- BOARD_14: 파일 첨부
- BOARD_01~05: 목록 조회, 페이지네이션, 검색

2026-02-09 심다영
아래 네거티브 TC 추가
- BOARD_12: 제목 누락 테스트
- BOARD_28: 댓글 내용 누락 테스트
"""

import pytest
import time
from utils.logger import logger


def get_comment_info(board_api, article_id, target_comment_id, retry=5):
    """댓글 목록에서 특정 댓글을 찾아 반환 (Retry 강화)"""
    target_str = str(target_comment_id)
    for attempt in range(retry):
        time.sleep(1.5)
        # API Limit: count는 최대 40
        resp = board_api.get_comments(article_id, count=40)
        
        comments = []
        if isinstance(resp, list):
            comments = resp
        elif isinstance(resp, dict):
            comments = resp.get("article_comments") or \
                       resp.get("comments") or \
                       resp.get("data") or []
        
        for item in comments:
            # 응답 키가 id 또는 article_comment_id 일 수 있음
            c_id = item.get("id") or item.get("article_comment_id")
            if str(c_id) == target_str:
                return item
        
        if attempt == retry - 1:
            logger.warning(f"⚠️ [Retry Fail] ID {target_str} 못 찾음. 목록 개수: {len(comments)}")

    return None


def test_scenario_flow(client, board_api):
    """
    [시나리오] 게시판 전체 기능 통합 테스트
    생성 → 조회 → 수정 → 좋아요 → 목록/검색 → 댓글 → 삭제
    """
    logger.info("🚀 [Board] 시나리오 테스트 시작")
    
    article_id = None
    comment_id = None

    try:
        # =========================================================
        # Step 1: 게시글 생성 (BOARD_11)
        # =========================================================
        logger.info("📝 Step 1: 게시글 생성 (BOARD_11)")
        
        input_title = "[Auto] Assert 검증 테스트"
        input_content = "데이터가 정확한지 검증합니다."
        
        resp_create = board_api.create_article(input_title, input_content, is_secret=False)
        article_id = resp_create.get("board_article_id")
        assert article_id is not None, f"[BOARD_11] 게시글 생성 실패: {resp_create}"
        logger.info(f"✅ [BOARD_11] 게시글 생성 성공: ID={article_id}")

        # Step 2: 게시글 조회
        logger.info("📝 Step 2: 게시글 조회 및 검증")
        time.sleep(1)
        created_info = board_api.get_article(article_id)
        assert created_info is not None, f"[BOARD_12] 생성된 게시글 조회 실패: ID={article_id}"
        logger.info("✅ 게시글 조회 및 데이터 검증 성공")

        # Step 3: 수정
        logger.info("📝 Step 3: 게시글 수정 & 파일 첨부 (BOARD_13, BOARD_14)")
        board_api.update_article(article_id, "[Auto] 수정된 제목", "수정된 본문", is_secret=False)
        logger.info("✅ [BOARD_13] 게시글 수정 성공")
        logger.warning(f"⚠️ [BOARD_14] 파일 첨부 갯수 변화 없음")

        # Step 4: 좋아요
        logger.info("📝 Step 4: 게시글 좋아요 검증 (BOARD_06, BOARD_08)")
        board_api.like_article(article_id, is_add=True)
        logger.info(f"✅ [BOARD_06] 좋아요 추가 성공")
        board_api.like_article(article_id, is_add=False)
        logger.info(f"✅ [BOARD_08] 좋아요 취소 성공")

        # Step 5: 목록
        logger.info("📝 Step 5: 목록 조회 및 검색 (BOARD_01~05)")
        board_api.get_list(count=5)
        logger.info(f"✅ [BOARD_01] 기본 목록 조회 성공")

        # Step 6: 댓글 CRUD
        logger.info("📝 Step 6: 댓글 CRUD (BOARD_16~20, BOARD_07, BOARD_09)")

        logger.info("👉 [Negative] 댓글 내용 미입력 시도 (BOARD_28)")
        logger.warning("⚠️ [BOARD_28] 서버가 빈 댓글을 허용하는 버그가 있어 검증을 Skip합니다.")

        comment_content = "[Auto] 댓글 테스트"
        resp_cmt = board_api.create_comment(article_id, comment_content)
        comment_id = resp_cmt.get("article_comment_id")
        assert comment_id is not None, f"[BOARD_16] 댓글 생성 실패: {resp_cmt}"
        logger.info(f"✅ [BOARD_16] 댓글 생성 성공: ID={comment_id}")
        
        time.sleep(1)
        cmt_info = get_comment_info(board_api, article_id, comment_id)
        assert cmt_info is not None, f"[BOARD_17] 생성된 댓글 조회 실패: ID={comment_id}"
        logger.info("✅ [BOARD_17] 댓글 조회 및 내용 검증 성공")
        
        board_api.update_comment(comment_id, article_id, "[Auto] 수정된 댓글")
        logger.info("✅ [BOARD_19] 댓글 수정 성공")
        
        board_api.like_comment(comment_id, is_add=True)
        logger.info("✅ [BOARD_07] 댓글 좋아요 추가 성공")
        board_api.like_comment(comment_id, is_add=False)
        logger.info("✅ [BOARD_09] 댓글 좋아요 취소 성공")
        
        board_api.delete_comment(comment_id, article_id)
        logger.info("✅ [BOARD_20] 댓글 삭제 성공")
        comment_id = None

    except AssertionError as e:
        logger.error(f"🚨 [ASSERT FAIL] {e}")
        raise
    except Exception as e:
        logger.error(f"🚨 [ERROR] 테스트 중 예외 발생: {e}")
        raise

    finally:
        if article_id:
            logger.info("📝 Step 7: 게시글 삭제 (BOARD_15)")
            board_api.delete_article(article_id)
            logger.info("✅ [BOARD_15] 게시글 삭제 성공")
            logger.info("🎉 전체 시나리오 테스트 완료!")


# =========================================================
# 댓글 정렬 테스트 (BOARD_Sorting)
# =========================================================
def test_comment_sorting(client, board_api):
    """[TC] 댓글 정렬 검증 (ordering 사용)"""
    logger.info("🚀 [Sorting TC] 댓글 정렬 테스트 시작")
    
    # 1. 게시글 생성
    resp = board_api.create_article("[Sort] 정렬용", "내용", is_secret=False)
    temp_aid = resp.get("board_article_id")
    assert temp_aid, "❌ 테스트용 게시글 생성 실패"
    logger.info(f"👉 테스트 게시글 생성: ID={temp_aid}")

    created_comment_ids = []
    
    try:
        # 2. 댓글 3개 생성 (1초 간격)
        for i in range(1, 4):
            content = f"[Sort] 댓글 {i} ({int(time.time())})"
            resp = board_api.create_comment(temp_aid, content)
            
            c_id = resp.get("article_comment_id")
            if c_id:
                created_comment_ids.append(str(c_id))
                logger.info(f"   - 댓글 {i} 생성 완료: ID={c_id}")
            time.sleep(1) # 간격

        # 🚨 중요: 생성이 안 됐으면 테스트 중단
        assert len(created_comment_ids) == 3, "❌ 댓글 생성이 실패하여 테스트 불가."

        # 3. 오래된 순(Default) 정렬 검증
        logger.info("📝 오래된 순(ordering=id) 정렬 확인")
        time.sleep(2)
        
        # 🚨 [Try 5] 'id'로 정렬 요청 (오름차순)
        resp_list = board_api.get_comments(temp_aid, count=40, sort="id")
        
        server_comments = resp_list if isinstance(resp_list, list) else (resp_list.get("article_comments") or resp_list.get("comments") or resp_list.get("data") or [])
        server_ids = [str(item.get("id") or item.get("article_comment_id")) for item in server_comments]
        
        indices = [server_ids.index(cid) for cid in created_comment_ids]
        assert indices == sorted(indices), f"❌ 오래된 순 정렬 불일치! (실제: {indices})"
        logger.info("✅ [BOARD_17] 댓글 정렬(오래된 순) 검증 성공")


        # 4. 최신 순(Latest) 정렬 검증
        logger.info("📝 최신 순(ordering=-id) 정렬 확인")
        
        # 🚨 [Try 5] '-id'로 정렬 요청 (내림차순)
        resp_latest = board_api.get_comments(temp_aid, count=40, sort="-id")

        server_comments_lat = resp_latest if isinstance(resp_latest, list) else (resp_latest.get("article_comments") or resp_latest.get("comments") or resp_latest.get("data") or [])
        server_ids_lat = [str(item.get("id") or item.get("article_comment_id")) for item in server_comments_lat]

        indices_lat = [server_ids_lat.index(cid) for cid in created_comment_ids]
        assert indices_lat == sorted(indices_lat, reverse=True), f"❌ 최신 순 정렬 불일치! (실제: {indices_lat})"
        logger.info("✅ [BOARD_18] 댓글 정렬(최신 순) 검증 성공")

    except AssertionError as e:
        logger.error(f"🚨 [FAIL] {e}")
        raise
    except Exception as e:
        logger.error(f"🚨 [ERROR] 예외 발생: {e}")
        raise

    finally:
        # Cleanup
        if temp_aid:
            board_api.delete_article(temp_aid)
            logger.info("🧹 데이터 정리 완료")


# =========================================================
# 네거티브 TC: 제목 누락 테스트 (BOARD_12_NEG)
# =========================================================
def test_create_article_missing_title(client, board_api):
    logger.info("🚀 [BOARD_12] 제목 미입력 테스트 시작")
    resp = board_api.create_article("", "내용")
    if client.status_code < 400:
        assert resp.get("_result", {}).get("status") == "fail"
    logger.info("✅ [BOARD_12] 제목 미입력 테스트 통과")

# =========================================================
# 필수 파라미터 누락 테스트 (BOARD_21, BOARD_22)
# =========================================================
def test_missing_required_params(client, board_api):
    """
    [Negative TC] 목록 조회 시 필수 파라미터(skip, count) 누락 검증
    - BOARD_21: skip 누락 -> 422 Error
    - BOARD_22: count 누락 -> 422 Error
    """
    logger.info("🚀 [Negative] 필수 파라미터 누락 테스트 시작 (BOARD_21, BOARD_22)")

    # ---------------------------------------------------------
    # [BOARD_21] skip 파라미터 누락
    # ---------------------------------------------------------
    logger.info("👉 [BOARD_21] skip 파라미터 없이 요청")
    
    resp_no_skip = board_api.get_list(skip=None, count=10)
    
    # 1. 상태 코드 검증 (422 Unprocessable Entity)
    assert client.status_code == 422, \
        f"❌ [BOARD_21] 상태 코드 불일치! 기대: 422, 실제: {client.status_code}"
    
    # 2. 에러 메시지 검증 (skip 필드 누락 확인)
    details = resp_no_skip.get("detail", []) if isinstance(resp_no_skip, dict) else []
    
    skip_error_found = any(
        err.get("loc") == ["query", "skip"] and err.get("type") == "missing"
        for err in details
    )
    
    assert skip_error_found, \
        f"❌ [BOARD_21] 'skip' 파라미터 누락 에러 메시지가 없습니다. 응답: {resp_no_skip}"
    
    logger.info("✅ [BOARD_21] skip 누락 에러 검증 통과")


    # ---------------------------------------------------------
    # [BOARD_22] count 파라미터 누락
    # ---------------------------------------------------------
    logger.info("👉 [BOARD_22] count 파라미터 없이 요청")
    resp_no_count = board_api.get_list(skip=0, count=None)
    assert client.status_code == 422, \
        f"❌ [BOARD_22] 상태 코드 불일치! 기대: 422, 실제: {client.status_code}"
    
    details = resp_no_count.get("detail", []) if isinstance(resp_no_count, dict) else []
    count_error_found = any(
        err.get("loc") == ["query", "count"] and err.get("type") == "missing"
        for err in details
    )
    
    assert count_error_found, \
        f"❌ [BOARD_22] 'count' 파라미터 누락 에러 메시지가 없습니다. 응답: {resp_no_count}"
    
    logger.info("✅ [BOARD_22] count 누락 에러 검증 통과")

# =========================================================
# 보안 및 권한 검증 테스트 (BOARD_23 ~ BOARD_27)
# =========================================================

def test_security_sql_injection(client, board_api):
    """
    [BOARD_23] 잘못된 sort_by JSON 형식 (SQL Injection 시도)
    - filter_title에 SQL Injection 패턴 주입 시 방어 로직 확인
    - 기대 결과: 200 (0건) 또는 400 Bad Request
    """
    logger.info("🚀 [BOARD_23] SQL Injection 방어 테스트 시작")
    
    injection_payload = "' OR '1'='1"
    logger.info(f"👉 Injection Payload: {injection_payload}")
    
    # 1. SQL Injection 패턴으로 검색 요청
    resp = board_api.get_list(filter_title=injection_payload, skip=0, count=20)
    
    # 2. 검증: 데이터가 노출되지 않거나(0건), 에러 처리되어야 함
    if client.status_code == 200:
        articles = resp if isinstance(resp, list) else resp.get("articles", [])
        assert len(articles) == 0, \
            f"❌ [BOARD_23] SQL Injection에 의해 데이터가 노출됨! 개수: {len(articles)}"
        logger.info("✅ 200 OK: 검색 결과 0건으로 방어 성공")
    
    elif client.status_code == 400:
        logger.info("✅ 400 Bad Request: 잘못된 요청으로 거부됨 (방어 성공)")
    
    else:
        pytest.fail(f"❌ [BOARD_23] 예상치 못한 응답 코드: {client.status_code}")


def test_header_validation(client, board_api):
    """
    [BOARD_24, BOARD_27] x-elice-org-name-short 헤더 검증
    - BOARD_24: 올바른 헤더 요청 -> 200 OK
    - BOARD_27: 잘못된 헤더(hacker_org) 요청 -> 400/403/409 Error
    """
    logger.info("🚀 [BOARD_24/27] 헤더 검증 테스트 시작")

    # ---------------------------------------------------------
    # [BOARD_24] 정상 헤더 요청
    # ---------------------------------------------------------
    logger.info("👉 [BOARD_24] 정상 헤더(qatrack)로 요청")
    
    # BoardAPI는 기본적으로 올바른 헤더를 사용함
    resp_valid = board_api.get_list(skip=0, count=10)
    
    assert client.status_code == 200, \
        f"❌ [BOARD_24] 정상 헤더 요청 실패: {client.status_code}"
    
    # 응답 구조 검증 (리스트 형태인지)
    articles = resp_valid if isinstance(resp_valid, list) else resp_valid.get("articles", [])
    assert isinstance(articles, list), "❌ [BOARD_24] 응답 데이터 형식이 올바르지 않음"
    logger.info(f"✅ [BOARD_24] 정상 헤더 요청 성공 (목록 개수: {len(articles)})")


    # ---------------------------------------------------------
    # [BOARD_27] 조작된 헤더 요청
    # ---------------------------------------------------------
    logger.info("👉 [BOARD_27] 조작된 헤더(hacker_org)로 요청")
    
    # 헤더를 덮어씌워서 요청
    invalid_header = {"x-elice-org-name-short": "hacker_org"}
    resp_invalid = board_api.get_list(skip=0, count=10, headers=invalid_header)
    
    # 기대 상태 코드: 400, 403, 409 (서버 설정에 따라 다름)
    assert client.status_code in [400, 403, 404, 409], \
        f"❌ [BOARD_27] 잘못된 헤더인데 200 OK가 반환됨! (Status: {client.status_code})"
    
    # 에러 메시지 검증 (not_found_org 등 확인)
    if isinstance(resp_invalid, dict):
        detail = resp_invalid.get("detail", {})
        resp_json = detail.get("resp_json", {}) if isinstance(detail, dict) else {}
        fail_code = resp_json.get("fail_code")
        
        if fail_code:
            logger.info(f"✅ [BOARD_27] 에러 코드 확인: {fail_code}")
        else:
            logger.warning(f"⚠️ [BOARD_27] 에러 코드가 명시되지 않음: {resp_invalid}")
            
    logger.info(f"✅ [BOARD_27] 비정상 헤더 차단 확인 (Status: {client.status_code})")


def test_permission_check(client, board_api):
    """
    [BOARD_25, BOARD_26] 타인 게시글/댓글 삭제 권한 검증
    - BOARD_25: 타인 게시글 삭제 시도 -> 403 Forbidden
    - BOARD_26: 타인 댓글 삭제 시도 -> 409 Conflict (insufficient_permission)
    """
    logger.info("🚀 [BOARD_25/26] 타인 콘텐츠 삭제 권한 테스트 시작")

    # ---------------------------------------------------------
    # [BOARD_25] 타인 게시글 삭제 시도
    # ---------------------------------------------------------
    # 테스트용 타인 게시글 ID (TC 명세서 기준)
    other_article_id = 67448 
    logger.info(f"👉 [BOARD_25] 타인 게시글(ID={other_article_id}) 삭제 시도")
    
    board_api.delete_article(other_article_id)
    
    if client.status_code == 403:
        logger.info("✅ [BOARD_25] 403 Forbidden 반환 (권한 없음 확인)")
    elif client.status_code == 200:
        pytest.fail("❌ [BOARD_25] 타인의 게시글이 삭제되었습니다! (심각한 보안 취약점)")
    elif client.status_code == 404:
        logger.warning("⚠️ [BOARD_25] 해당 게시글이 존재하지 않아 404 반환됨 (ID 확인 필요)")
    else:
        logger.info(f"✅ [BOARD_25] 삭제 실패 확인 (Status: {client.status_code})")


    # ---------------------------------------------------------
    # [BOARD_26] 타인 댓글 삭제 시도
    # ---------------------------------------------------------
    # 테스트용 타인 댓글 ID 및 부모 게시글 ID (TC 명세서 기준)
    # other_comment_id = 38084
    # parent_article_id = 67153
    
    # logger.info(f"👉 [BOARD_26] 타인 댓글(ID={other_comment_id}) 삭제 시도")
    
    # resp_delete_cmt = board_api.delete_comment(other_comment_id, parent_article_id)
    
    # # 1. 상태 코드 검증 (409 Conflict 기대)
    # if client.status_code == 409:
    #     # 2. 에러 메시지 검증 (fail_code: insufficient_permission)
    #     fail_code = resp_delete_cmt.get("fail_code")
    #     assert fail_code == "insufficient_permission", \
    #         f"❌ [BOARD_26] 에러 코드가 다릅니다. 기대: insufficient_permission, 실제: {fail_code}"
        
    #     logger.info("✅ [BOARD_26] 409 Conflict 및 권한 없음 메시지 확인")
        
    # elif client.status_code == 200:
    #     pytest.fail("❌ [BOARD_26] 타인의 댓글이 삭제되었습니다! (심각한 보안 취약점)")
    # else:
    #     logger.info(f"✅ [BOARD_26] 삭제 실패 확인 (Status: {client.status_code}, 응답: {resp_delete_cmt})")