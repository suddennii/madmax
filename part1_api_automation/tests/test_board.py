"""
게시판(Board) API 테스트 - TC 기반 통합 시나리오

작성자: 심다영 / 작성일: 2026-02-05
수정자: 심다영 / 수정일: 2026-02-11

[테스트 범위]
- Positive: BOARD_01~20 (시나리오, 정렬)
- Negative: BOARD_12, BOARD_21~28 (필수값, 보안, 권한)
- Security: 타인 계정 사칭(Impersonation) 추가

[결과 처리 기준]
- PASS: 기대대로 동작
- FAIL: 버그 발견 (CI/CD 배포 차단)
- XFAIL: 알려진 버그, 수정 예정 (pytest.mark.xfail)
- SKIP: 환경 문제로 테스트 불가
- WARNING: 잠재적 이슈지만 테스트는 통과 (로그만 남김)

[설정 변경 방법]
- STRICT_MODE = True  → 애매한 케이스도 FAIL 처리
- STRICT_MODE = False → 애매한 케이스는 WARNING 처리 (기본값)
"""

import pytest
import time

from utils.logger import logger
from utils.config import REST_BASE_URL, CLASSROOM_ID, ACCOUNT_ID, ACCOUNT_ID2


# =============================================================================
# ⚙️ [설정 영역
# =============================================================================

#  안전 사용자 목록 (타인 게시글 삭제 테스트에서 제외할 사용자)
SAFE_USERS = ["심다영", "[매니저]송찬영"]

#  엄격 모드 설정
# - True: 애매한 케이스(작성자 확인 불가 등)도 FAIL 처리
# - False: 애매한 케이스는 WARNING만 남기고 PASS 처리 (기본값)
STRICT_MODE = False

#  특정 게시글 ID (댓글 사칭 테스트용)
TARGET_ARTICLE_ID_FOR_COMMENT_TEST = 67606

#  알려진 버그 목록 (XFAIL 처리할 테스트)
# - 버그가 수정되면 해당 항목을 주석 처리하거나 삭제하세요
KNOWN_BUGS = {
    # "test_create_comment_missing_content": "JIRA-1234: 빈 댓글 허용 버그, 2/15 수정 예정",
    # "test_create_article_missing_title": "JIRA-1235: 빈 제목 허용 버그",
}


# =============================================================================
#  보조 함수
# =============================================================================

def _extract_author_name(article):
    """게시글/댓글에서 작성자 이름 추출"""
    user = article.get("user") or article.get("account") or article.get("author") or {}
    return user.get("fullname") or user.get("name") or article.get("author_name") or "Unknown"


def _extract_author_id(article):
    """게시글/댓글에서 작성자 ID 추출"""
    user = article.get("user") or article.get("account") or {}
    return user.get("id") or article.get("created_by")


def _parse_article_list(response):
    """API 응답에서 게시글 리스트 추출 (에러 시 None 반환)"""
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        if response.get("_result", {}).get("status") == "fail":
            return None
        return response.get("articles") or response.get("data") or []
    return []


def _parse_comment_list(response):
    """API 응답에서 댓글 리스트 추출"""
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        return (response.get("article_comments") or 
                response.get("comments") or 
                response.get("data") or [])
    return []


def get_comment_info(board_api, article_id, target_comment_id, retry=5):
    """댓글 목록에서 특정 댓글을 찾아 반환"""
    target_str = str(target_comment_id)
    
    for _ in range(retry):
        time.sleep(1)
        comments = _parse_comment_list(board_api.get_comments(article_id, count=40))
        
        for item in comments:
            c_id = item.get("id") or item.get("article_comment_id")
            if str(c_id) == target_str:
                return item
    
    return None


def find_other_user_article(board_api, safe_users=SAFE_USERS, max_pages=3):
    """타인의 게시글을 자동으로 찾아 반환"""
    PAGE_SIZE = 40
    
    for page in range(max_pages):
        skip = page * PAGE_SIZE
        logger.info(f"📄 페이지 {page + 1} 탐색 중... (skip={skip})")
        
        articles = _parse_article_list(board_api.get_list(skip=skip, count=PAGE_SIZE))
        
        if articles is None:
            logger.error("❌ API 에러 발생")
            return None
        
        if not articles:
            break
        
        for article in articles:
            author = _extract_author_name(article)
            
            if author not in safe_users and author != "Unknown":
                logger.info(f"🎯 타겟 발견! 작성자: '{author}', 글ID: {article.get('id')}")
                return {
                    "id": article.get("id"),
                    "author": author,
                    "title": article.get("title", "제목없음")
                }
    
    return None


# =============================================================================
# ✅ [Positive] 통합 시나리오 테스트
# 
# 결과 처리:
# - 모든 Step 통과 → PASS
# - 어느 하나라도 실패 → FAIL (AssertionError)
# =============================================================================

def test_scenario_flow(client, board_api):
    """
    [시나리오] 게시판 전체 기능 통합 테스트
    생성 → 조회 → 수정 → 좋아요 → 목록/검색 → 댓글 → 삭제
    """
    logger.info("🚀 [Board] 시나리오 테스트 시작")
    
    article_id = None
    comment_id = None

    try:
        # Step 1: 게시글 생성 (BOARD_11)
        logger.info("📝 Step 1: 게시글 생성 (BOARD_11)")
        
        input_title = "[Auto] Assert 검증 테스트"
        input_content = "데이터가 정확한지 검증합니다."
        
        resp_create = board_api.create_article(input_title, input_content, is_secret=False)
        
        # ❌ FAIL 조건: API 에러 발생
        assert "_result" not in resp_create or resp_create.get("_result", {}).get("status") != "fail", \
            f"[BOARD_11] API 에러 발생: {resp_create}"
        
        article_id = resp_create.get("board_article_id")
        
        # ❌ FAIL 조건: ID 없음
        assert article_id is not None, f"[BOARD_11] 게시글 ID 없음: {resp_create}"
        logger.info(f"✅ [BOARD_11] 게시글 생성 성공: ID={article_id}")

        # Step 2: 게시글 조회 및 검증 (BOARD_12)
        logger.info("📝 Step 2: 게시글 조회 및 검증")
        time.sleep(0.5)
        created_info = board_api.get_article(article_id)
        
        assert created_info is not None, f"[BOARD_12] 게시글 조회 실패: ID={article_id}"
        assert created_info.get("title") == input_title, "[BOARD_12] 제목 불일치"
        logger.info("✅ 게시글 조회 및 데이터 검증 성공")

        # Step 3: 게시글 수정 (BOARD_13, BOARD_14)
        logger.info("📝 Step 3: 게시글 수정 (BOARD_13, BOARD_14)")
        
        update_title = "[Auto] 수정된 제목"
        attachment_before = created_info.get("article_attachment_count", 0)
        
        test_files = {'file': ('test.txt', 'Test content', 'text/plain')}
        board_api.update_article(article_id, update_title, "수정된 본문", is_secret=False, files=test_files)
        
        assert board_api.status_code == 200, f"[BOARD_13] 수정 실패: {board_api.status_code}"
        
        time.sleep(1)
        updated_info = board_api.get_article(article_id)
        assert updated_info.get("title") == update_title, "[BOARD_13] 제목 수정 실패"
        logger.info("✅ [BOARD_13] 게시글 수정 성공")
        
        # ⚠️ WARNING 처리: 파일 첨부 실패는 경고만
        attachment_after = updated_info.get("article_attachment_count", 0)
        if attachment_after > attachment_before:
            logger.info(f"✅ [BOARD_14] 파일 첨부 성공")
        else:
            logger.warning(f"⚠️ [BOARD_14] 파일 첨부 갯수 변화 없음 (서버 설정 확인 필요)")

        # Step 4: 게시글 좋아요 (BOARD_06, BOARD_08)
        logger.info("📝 Step 4: 게시글 좋아요 (BOARD_06, BOARD_08)")
        
        likes_before = updated_info.get("like_count", 0)
        board_api.like_article(article_id, is_add=True)
        assert board_api.status_code == 200, "[BOARD_06] 좋아요 추가 실패"
        
        time.sleep(1)
        info_after = board_api.get_article(article_id)
        likes_after = info_after.get("like_count", 0)
        assert likes_after == likes_before + 1, f"[BOARD_06] 좋아요 증가 실패"
        logger.info(f"✅ [BOARD_06] 좋아요 추가 성공: {likes_before} → {likes_after}")
        
        board_api.like_article(article_id, is_add=False)
        assert board_api.status_code == 200, "[BOARD_08] 좋아요 취소 실패"
        logger.info("✅ [BOARD_08] 좋아요 취소 성공")

        # Step 5: 목록 조회 및 검색 (BOARD_01~05)
        logger.info("📝 Step 5: 목록 조회 및 검색 (BOARD_01~05)")
        
        articles = board_api.get_list(skip=0, count=10)
        articles = articles if isinstance(articles, list) else []
        assert len(articles) > 0, "[BOARD_01] 목록이 비어있음"
        logger.info(f"✅ [BOARD_01] 기본 목록 조회 성공: {len(articles)}개")
        
        page1 = board_api.get_list(skip=0, count=5)
        page2 = board_api.get_list(skip=5, count=5)
        p1_ids = {a.get("id") for a in (page1 if isinstance(page1, list) else [])}
        p2_ids = {a.get("id") for a in (page2 if isinstance(page2, list) else [])}
        assert len(p1_ids & p2_ids) == 0, "[BOARD_02] 페이지네이션 중복"
        logger.info("✅ [BOARD_02] 페이지네이션 성공")
        
        search = board_api.get_list(filter_title="%Auto%")
        search = search if isinstance(search, list) else []
        assert len(search) > 0, "[BOARD_03] 검색 결과 없음"
        logger.info(f"✅ [BOARD_03] 검색 성공: {len(search)}개")
        
        no_result = board_api.get_list(filter_title="%zzznotexist%")
        no_result = no_result if isinstance(no_result, list) else []
        assert len(no_result) == 0, "[BOARD_04] 없는 키워드 결과 있음"
        logger.info("✅ [BOARD_04] 검색 (없는 키워드) 성공")

        # Step 6: 댓글 CRUD (BOARD_16~20, BOARD_07, BOARD_09)
        logger.info("📝 Step 6: 댓글 CRUD")

        comment_content = "[Auto] 댓글 테스트"
        resp_cmt = board_api.create_comment(article_id, comment_content)
        comment_id = resp_cmt.get("article_comment_id")
        assert comment_id is not None, f"[BOARD_16] 댓글 생성 실패: {resp_cmt}"
        logger.info(f"✅ [BOARD_16] 댓글 생성 성공: ID={comment_id}")
        
        time.sleep(1)
        
        cmt_info = get_comment_info(board_api, article_id, comment_id)
        assert cmt_info is not None, f"[BOARD_17] 댓글 조회 실패"
        assert cmt_info.get("content") == comment_content, "[BOARD_17] 댓글 내용 불일치"
        logger.info("✅ [BOARD_17] 댓글 조회 성공")
        
        board_api.update_comment(comment_id, article_id, "[Auto] 수정된 댓글")
        assert board_api.status_code == 200, "[BOARD_19] 댓글 수정 실패"
        logger.info("✅ [BOARD_19] 댓글 수정 성공")
        
        cmt_before = get_comment_info(board_api, article_id, comment_id)
        cmt_likes_before = cmt_before.get("comment_like_count", 0) if cmt_before else 0
        
        board_api.like_comment(comment_id, is_add=True)
        assert board_api.status_code == 200, "[BOARD_07] 댓글 좋아요 추가 실패"
        
        time.sleep(1)
        cmt_after = get_comment_info(board_api, article_id, comment_id)
        cmt_likes_after = cmt_after.get("comment_like_count", 0) if cmt_after else 0
        assert cmt_likes_after == cmt_likes_before + 1, "[BOARD_07] 댓글 좋아요 증가 실패"
        logger.info(f"✅ [BOARD_07] 댓글 좋아요 추가 성공")
        
        board_api.like_comment(comment_id, is_add=False)
        assert board_api.status_code == 200, "[BOARD_09] 댓글 좋아요 취소 실패"
        logger.info("✅ [BOARD_09] 댓글 좋아요 취소 성공")
        
        board_api.delete_comment(comment_id, article_id)
        assert board_api.status_code == 200, "[BOARD_20] 댓글 삭제 실패"
        
        time.sleep(1)
        deleted_cmt = get_comment_info(board_api, article_id, comment_id)
        assert deleted_cmt is None, "[BOARD_20] 댓글 삭제 안됨"
        logger.info("✅ [BOARD_20] 댓글 삭제 성공")
        comment_id = None

    except AssertionError as e:
        logger.error(f"🚨 [ASSERT FAIL] {e}")
        raise
    except Exception as e:
        logger.error(f"🚨 [ERROR] {e}")
        raise

    finally:
        if article_id:
            logger.info("📝 Step 7: 게시글 삭제 (BOARD_15)")
            board_api.delete_article(article_id)
            assert board_api.status_code == 200, "[BOARD_15] 게시글 삭제 실패"
            
            time.sleep(1)
            deleted = board_api.get_article(article_id)
            assert deleted is None, "[BOARD_15] 게시글 삭제 안됨"
            logger.info("✅ [BOARD_15] 게시글 삭제 성공")
            logger.info("🎉 전체 시나리오 테스트 완료!")


# =============================================================================
# ✅ [Positive] 댓글 정렬 테스트 (BOARD_17, BOARD_18)
# 
# 결과 처리:
# - 정렬 순서 일치 → PASS
# - 정렬 순서 불일치 → FAIL
# =============================================================================

def test_comment_sorting(client, board_api):
    """[TC] 댓글 정렬 검증"""
    logger.info("🚀 [Sorting TC] 댓글 정렬 테스트 시작")
    
    resp = board_api.create_article("[Sort] 정렬용", "내용", is_secret=False)
    temp_aid = resp.get("board_article_id")
    assert temp_aid, f"❌ 게시글 생성 실패: {resp}"
    logger.info(f"👉 테스트 게시글: ID={temp_aid}")

    created_ids = []
    
    try:
        for i in range(1, 4):
            resp = board_api.create_comment(temp_aid, f"[Sort] 댓글 {i}")
            c_id = resp.get("article_comment_id")
            if c_id:
                created_ids.append(str(c_id))
                logger.info(f"   - 댓글 {i}: ID={c_id}")
            time.sleep(0.1)

        time.sleep(2)

        # 오래된 순 정렬 검증
        logger.info("👉 오래된 순(ASC) 정렬 요청 (sort='id')")
        comments = _parse_comment_list(board_api.get_comments(temp_aid, count=40, sort="id"))
        server_ids = [str(c.get("id") or c.get("article_comment_id")) for c in comments]
        
        indices = [server_ids.index(cid) for cid in created_ids if cid in server_ids]
        if len(indices) == 3:
            assert indices == sorted(indices), f"❌ 오래된순 정렬 불일치 (실제: {indices})"
            logger.info("✅ [BOARD_17] 오래된순 정렬 성공")

        # 최신 순 정렬 검증
        logger.info("👉 최신 순(DESC) 정렬 요청 (sort='-id')")
        comments_lat = _parse_comment_list(board_api.get_comments(temp_aid, count=40, sort="-id"))
        server_ids_lat = [str(c.get("id") or c.get("article_comment_id")) for c in comments_lat]
        
        indices_lat = [server_ids_lat.index(cid) for cid in created_ids if cid in server_ids_lat]
        if len(indices_lat) == 3:
            assert indices_lat == sorted(indices_lat, reverse=True), f"❌ 최신순 정렬 불일치 (실제: {indices_lat})"
            logger.info("✅ [BOARD_18] 최신순 정렬 성공")

    finally:
        if temp_aid:
            board_api.delete_article(temp_aid)
            logger.info("🧹 정리 완료")


# =============================================================================
# 🔒 [Security] 타인 계정 사칭 글쓰기 (BOARD_29)
# 
# 결과 처리:
# - 서버가 거부하거나, 내 ID로 등록됨 → PASS (보안 양호)
# - 타인 ID로 등록됨 → FAIL (🚨 심각한 보안 취약점)
# - 작성자 ID 확인 불가 → STRICT_MODE에 따라 FAIL 또는 WARNING
# =============================================================================

def test_security_impersonation(board_api):
    """[Security TC] 타인 계정 사칭 글쓰기 시도"""
    logger.info("🚀 [Security] 타인 ID 사칭 글쓰기 테스트 시작")

    if not ACCOUNT_ID2:
        pytest.skip("ACCOUNT_ID2가 설정되지 않음")

    victim_id = ACCOUNT_ID2 
    logger.info(f"👉 내 ID: {ACCOUNT_ID}, 공격 대상(타인) ID: {victim_id}")

    payload = {
        "title": "[Security] 사칭 테스트",
        "content": f"이 글은 {ACCOUNT_ID}가 {victim_id} 명의로 작성을 시도한 글입니다.",
        "classroom_id": CLASSROOM_ID,
        "is_secret": "false",
        "account_id": victim_id,
        "user_id": victim_id,
        "writer_id": victim_id,
        "created_by": victim_id,
        "author_id": victim_id,
        "user": {"id": victim_id}
    }

    full_url = f"{REST_BASE_URL}{board_api.WRITE_PATH}/edit/"
    resp = board_api._send_request("POST", full_url, payload=payload)

    new_article_id = resp.get("board_article_id")
    
    # ✅ PASS: 서버가 요청 거부
    if board_api.status_code >= 400:
        logger.info(f"✅ 서버가 요청을 거부함 (Status: {board_api.status_code}) - 보안 양호")
        return

    if not new_article_id:
        logger.warning(f"⚠️ 글 생성 실패 또는 응답 구조 다름: {resp}")
        return

    try:
        time.sleep(1)
        created_article = board_api.get_article(new_article_id)
        real_author_id = _extract_author_id(created_article)

        # ❌ FAIL: 타인 ID로 등록됨
        if str(real_author_id) == str(victim_id):
            pytest.fail(f"🚨 [CRITICAL] 사칭 성공! 내 토큰으로 {victim_id} 님의 글이 작성되었습니다.")
        
        # ✅ PASS: 내 ID로 등록됨
        elif str(real_author_id) == str(ACCOUNT_ID):
            logger.info(f"✅ 사칭 실패: 입력한 ID({victim_id}) 무시됨. 내 ID({real_author_id})로 등록 - 보안 양호")
        
        # ⚠️ 작성자 ID 확인 불가
        else:
            # 🔧 [관리 포인트] STRICT_MODE에 따라 처리
            if STRICT_MODE:
                pytest.fail(f"❌ 작성자 ID 확인 불가: {real_author_id} (STRICT_MODE=True)")
            else:
                logger.warning(f"⚠️ 작성자 ID 확인 불가 (응답: {real_author_id}) - API 응답 구조 확인 필요")

    finally:
        if new_article_id:
            board_api.delete_article(new_article_id)
            logger.info("🧹 보안 테스트용 글 삭제 완료")


# =============================================================================
# ❌ [Negative] 제목 누락 테스트 (BOARD_12)
# 
# 결과 처리:
# - 서버가 거부 → PASS (정상)
# - 빈 제목이 허용됨 → FAIL (Validation 버그)
# =============================================================================

def test_create_article_missing_title(client, board_api):
    """[Negative] 제목 미입력 시 에러 응답 확인"""
    
    # 🔧 [관리 포인트] 알려진 버그면 XFAIL 처리
    if "test_create_article_missing_title" in KNOWN_BUGS:
        pytest.xfail(KNOWN_BUGS["test_create_article_missing_title"])
    
    logger.info("🚀 [BOARD_12] 제목 미입력 테스트")
    resp = board_api.create_article("", "내용")
    
    # ✅ PASS: HTTP 에러 코드로 거부
    if board_api.status_code >= 400:
        logger.info(f"✅ 서버가 {board_api.status_code} 에러 반환 - 정상")
        return
    
    # ✅ PASS: body에서 fail 상태로 거부
    if resp.get("_result", {}).get("status") == "fail":
        logger.info("✅ 응답 내 fail 상태 확인 - 정상")
        return
    
    # ❌ FAIL: 빈 제목이 허용됨
    aid = resp.get("board_article_id")
    if aid:
        board_api.delete_article(aid)
        pytest.fail(
            f"🚨 [BOARD_12] 버그 발견: 빈 제목의 게시글이 생성되었습니다! (ID={aid})\n"
            f"서버가 title 필수값 검증을 하지 않습니다."
        )
    
    logger.info("✅ [BOARD_12] 테스트 완료")


# =============================================================================
# ❌ [Negative] 필수 파라미터 누락 (BOARD_21, BOARD_22)
# 
# 결과 처리:
# - 422 에러 반환 → PASS
# - 다른 상태 코드 → FAIL
# =============================================================================

def test_missing_required_params(client, board_api):
    """[Negative] 목록 조회 시 필수 파라미터 누락 검증"""
    logger.info("🚀 [Negative] 필수 파라미터 누락 테스트")

    logger.info("👉 [BOARD_21] skip 없이 요청")
    board_api.get_list(skip=None, count=10)
    assert board_api.status_code == 422, f"❌ [BOARD_21] 기대: 422, 실제: {board_api.status_code}"
    logger.info("✅ [BOARD_21] 통과")

    logger.info("👉 [BOARD_22] count 없이 요청")
    board_api.get_list(skip=0, count=None)
    assert board_api.status_code == 422, f"❌ [BOARD_22] 기대: 422, 실제: {board_api.status_code}"
    logger.info("✅ [BOARD_22] 통과")


# =============================================================================
# 🔒 [Security] SQL Injection 방어 (BOARD_23)
# 
# 결과 처리:
# - 검색 결과 0건 또는 400 에러 → PASS (방어 성공)
# - 데이터 노출 → FAIL (🚨 SQL Injection 취약점!)
# =============================================================================

def test_security_sql_injection(client, board_api):
    """[Security] SQL Injection 방어 테스트"""
    logger.info("🚀 [BOARD_23] SQL Injection 방어 테스트")
    
    payload = "' OR '1'='1"
    resp = board_api.get_list(filter_title=payload, skip=0, count=20)
    
    # ✅ PASS: 200이지만 결과 0건
    if board_api.status_code == 200:
        articles = resp if isinstance(resp, list) else []
        assert len(articles) == 0, f"🚨 [BOARD_23] SQL Injection 취약점! 데이터 노출: {len(articles)}건"
        logger.info("✅ 검색 결과 0건 (방어 성공)")
        return
    
    # ✅ PASS: 400 에러로 거부
    if board_api.status_code == 400:
        logger.info("✅ 400 에러 (방어 성공)")
        return
    
    # ❌ FAIL: 예상치 못한 응답
    pytest.fail(f"❌ [BOARD_23] 예상치 못한 응답: {board_api.status_code}")


# =============================================================================
# ❌ [Negative] 헤더 검증 (BOARD_24, BOARD_27)
# 
# 결과 처리:
# - 정상 헤더 200 & 조작 헤더 차단 → PASS
# - 정상 헤더 실패 또는 조작 헤더 허용 → FAIL
# =============================================================================

def test_header_validation(client, board_api):
    """[Negative] x-elice-org-name-short 헤더 검증"""
    logger.info("🚀 [BOARD_24/27] 헤더 검증 테스트")

    logger.info("👉 [BOARD_24] 정상 헤더")
    board_api.get_list(skip=0, count=10)
    assert board_api.status_code == 200, f"❌ [BOARD_24] 정상 요청 실패: {board_api.status_code}"
    logger.info("✅ [BOARD_24] 성공")

    logger.info("👉 [BOARD_27] 조작된 헤더")
    board_api.get_list(skip=0, count=10, headers={"x-elice-org-name-short": "hacker"})
    assert board_api.status_code in [400, 403, 404, 409], \
        f"🚨 [BOARD_27] 조작된 헤더가 허용됨! (Status: {board_api.status_code})"
    logger.info(f"✅ [BOARD_27] 차단 확인 ({board_api.status_code})")


# =============================================================================
# 🔒 [Security] 타인 게시글 삭제 권한 검증 - 자동 탐지 (BOARD_25)
# 
# 결과 처리:
# - 서버가 삭제 거부 → PASS (보안 양호)
# - 타인 게시글 삭제됨 → FAIL (🚨🚨🚨 심각한 보안 취약점!)
# - 타인 게시글 없음 → SKIP
# =============================================================================

def test_delete_other_user_article_auto(client, board_api):
    """[BOARD_25] 타인 게시글 삭제 권한 검증 (자동 탐지)"""
    logger.info("🚀 [BOARD_25] 타인 게시글 삭제 권한 테스트 (자동 탐지)")
    logger.info(f"📋 안전 사용자 목록: {SAFE_USERS}")
    
    target = find_other_user_article(board_api, SAFE_USERS)
    
    if target is None:
        logger.warning("⚠️ 타인의 게시글을 찾지 못했습니다.")
        pytest.skip("삭제 테스트 대상을 찾지 못함")
        return
    
    target_id, target_author, target_title = target["id"], target["author"], target["title"]
    
    logger.info(f"🎯 삭제 시도 대상: ID={target_id}, 작성자={target_author}, 제목={target_title}")
    logger.info(f"🗑️ 삭제 API 호출...")
    
    resp = board_api.delete_article(target_id)
    status = board_api.status_code
    
    logger.info(f"📡 응답: {status} / {resp}")
    
    # ✅ PASS: body에서 fail 상태로 거부
    if isinstance(resp, dict) and resp.get("_result", {}).get("status") == "fail":
        logger.info(f"✅ [보안 양호] 서버가 삭제를 거부함 (fail_code: {resp.get('fail_code')})")
        return
    
    # ✅ PASS: HTTP 상태 코드로 거부
    if status in [401, 403, 409]:
        logger.info(f"✅ [보안 양호] {status} 에러 - 권한 없음")
        return
    
    if status == 404:
        logger.warning("⚠️ 404 Not Found - 게시글이 이미 존재하지 않음")
        return
    
    # ⚠️ 200 OK → 실제 삭제 여부 확인
    if status == 200:
        logger.warning("⚠️ 200 OK가 반환됨! 실제 삭제 여부 확인 중...")
        time.sleep(1)
        
        if board_api.get_article(target_id) is None:
            # ❌ FAIL: 실제로 삭제됨
            pytest.fail(
                f"🚨🚨🚨 [보안 취약점 발견] 🚨🚨🚨\n"
                f"타인({target_author})의 게시글(ID={target_id})이 삭제되었습니다!\n"
                f"제목: {target_title}"
            )
        else:
            logger.warning("⚠️ 200 OK가 왔지만 실제로 삭제되지 않음")
            logger.info("✅ 게시글은 여전히 존재함 - 보안상 문제없음")
    else:
        logger.info(f"✅ [보안 양호] 삭제 실패 (상태 코드: {status})")


# =============================================================================
# 🔍 [Debug] 게시글 작성자 정보 구조 확인
# 
# 결과 처리: 항상 PASS (디버그용)
# =============================================================================

def test_delete_other_user_article_debug(client, board_api):
    """[디버그용] 게시글 목록의 작성자 정보 구조 확인"""
    logger.info("🔍 [Debug] 게시글 작성자 정보 구조 확인")
    
    articles = _parse_article_list(board_api.get_list(skip=0, count=5))
    
    if not articles:
        logger.info("❌ 게시글이 없습니다.")
        return
    
    logger.info(f"📋 첫 번째 게시글 주요 필드:")
    first = articles[0]
    for key in ["user", "account", "author", "writer"]:
        if key in first:
            logger.info(f"   🔑 {key}: {first[key]}")
    
    logger.info(f"\n📋 처음 5개 게시글 작성자 정보:")
    for i, article in enumerate(articles[:5], 1):
        author = _extract_author_name(article)
        logger.info(f"   {i}. ID={article.get('id')}, 작성자='{author}', 제목='{article.get('title', '')[:20]}'")


# =============================================================================
# ❌ [Negative] 댓글 내용 미입력 (BOARD_28)
# 
# 결과 처리:
# - 서버가 거부 → PASS (정상)
# - 빈 댓글 허용됨 → FAIL (Validation 버그)
# =============================================================================

def test_create_comment_missing_content(client, board_api):
    """[Negative] 댓글 내용 미입력 시 에러 응답 확인"""
    
    # 🔧 [관리 포인트] 알려진 버그면 XFAIL 처리
    if "test_create_comment_missing_content" in KNOWN_BUGS:
        pytest.xfail(KNOWN_BUGS["test_create_comment_missing_content"])
    
    logger.info("🚀 [BOARD_28] 댓글 내용 미입력 테스트")
    
    resp = board_api.create_article("[Test] 댓글용", "내용", is_secret=False)
    temp_aid = resp.get("board_article_id")
    
    if not temp_aid:
        pytest.skip(f"게시글 생성 실패: {resp}")
    
    try:
        resp_cmt = board_api.create_comment(temp_aid, "")
        
        # ✅ PASS: HTTP 에러 코드로 거부
        if board_api.status_code >= 400:
            logger.info(f"✅ 서버가 {board_api.status_code} 에러 반환 - 정상")
            return
        
        # ✅ PASS: body에서 fail 상태로 거부
        if resp_cmt.get("_result", {}).get("status") == "fail":
            logger.info("✅ 응답 내 fail 상태 확인 - 정상")
            return
        
        # ❌ FAIL: 빈 댓글이 허용됨
        comment_id = resp_cmt.get("article_comment_id")
        if comment_id:
            board_api.delete_comment(comment_id, temp_aid)
            pytest.fail(
                f"🚨 [BOARD_28] 버그 발견: 빈 댓글이 생성되었습니다! (ID={comment_id})\n"
                f"서버가 content 필수값 검증을 하지 않습니다."
            )
        
    finally:
        if temp_aid:
            board_api.delete_article(temp_aid)
    
    logger.info("✅ [BOARD_28] 테스트 완료")


# =============================================================================
# 🔒 [Security] 특정 게시글에 타인 계정 댓글 사칭 시도 (BOARD_30)
# 
# 결과 처리:
# - 서버가 거부하거나, 내 ID로 등록됨 → PASS (보안 양호)
# - 타인 ID로 등록됨 → FAIL (🚨 심각한 보안 취약점)
# - 작성자 ID 확인 불가 → STRICT_MODE에 따라 FAIL 또는 WARNING
# =============================================================================

def test_security_comment_impersonation_fixed_article(board_api):
    """[Security TC] 지정된 게시글에 타인 ID로 댓글 작성 시도"""
    target_article_id = TARGET_ARTICLE_ID_FOR_COMMENT_TEST
    
    if not ACCOUNT_ID2:
        pytest.skip("ACCOUNT_ID2(타인 ID)가 설정되지 않음")

    victim_id = ACCOUNT_ID2
    logger.info(f"🚀 [Security] 게시글 {target_article_id}번에 타인({victim_id}) 명의 댓글 작성 시도")

    comment_id = None

    try:
        payload = {
            "board_article_id": target_article_id,
            "content": f"[Security] {ACCOUNT_ID}가 {victim_id} 님인 척 작성한 댓글입니다.",
            "classroom_id": CLASSROOM_ID,
            "is_secret": "false",
            "account_id": victim_id,
            "user_id": victim_id,
            "writer_id": victim_id,
            "created_by": victim_id,
            "author_id": victim_id,
            "user": {"id": victim_id}
        }

        url = f"{REST_BASE_URL}{board_api.WRITE_PATH}/comment/edit/"
        resp = board_api._send_request("POST", url, payload=payload)

        # ✅ PASS: 서버가 요청 거부
        if board_api.status_code >= 400:
            logger.info(f"✅ 서버가 요청을 거부함 (Status: {board_api.status_code}) - 보안 양호")
            return

        comment_id = resp.get("article_comment_id")
        if not comment_id:
            logger.warning(f"⚠️ 댓글 생성 실패 또는 응답 구조 다름: {resp}")
            return
        
        logger.info(f"👉 댓글이 생성되었습니다! ID: {comment_id}")
        time.sleep(1)
        
        comments = _parse_comment_list(board_api.get_comments(target_article_id, count=10, sort="-id"))
        target_comment = next((c for c in comments if str(c.get("id") or c.get("article_comment_id")) == str(comment_id)), None)
        
        if not target_comment:
            logger.warning(f"⚠️ 목록에서 방금 쓴 댓글({comment_id})을 찾을 수 없습니다.")
            return

        real_author_id = _extract_author_id(target_comment)
        logger.info(f"🕵️‍♂️ 실제 작성자: {real_author_id} / 공격 대상: {victim_id}")

        # ❌ FAIL: 타인 ID로 등록됨
        if str(real_author_id) == str(victim_id):
            pytest.fail(f"🚨 [CRITICAL] 사칭 성공! {victim_id} 님의 이름으로 댓글이 등록되었습니다.")
        
        # ✅ PASS: 내 ID로 등록됨
        elif str(real_author_id) == str(ACCOUNT_ID):
            logger.info("✅ 사칭 실패: 입력한 ID는 무시되고 '내 ID'로 정상 등록됨 - 보안 양호")
        
        # ⚠️ 작성자 ID 확인 불가
        else:
            if STRICT_MODE:
                pytest.fail(f"❌ 작성자 ID 확인 불가: {real_author_id} (STRICT_MODE=True)")
            else:
                logger.warning(f"⚠️ 작성자 ID 확인 불가: {real_author_id} - API 응답 구조 확인 필요")

    finally:
        if comment_id:
            board_api.delete_comment(comment_id, target_article_id)
            logger.info(f"🧹 테스트용 댓글({comment_id}) 삭제 완료")