"""
게시판(Board) API 테스트 - TC 기반 통합 시나리오

작성자: 심다영 / 작성일: 2026-02-05
수정자: 심다영 / 수정일: 2026-02-10

[테스트 범위]
- Positive: BOARD_01~20 (시나리오, 정렬)
- Negative: BOARD_12, BOARD_21~28 (필수값, 보안, 권한)
- Security: 타인 계정 사칭(Impersonation) 추가

[설정]
- 대기 방식: time.sleep (안정성 확보)
"""

import pytest
import time
from utils.logger import logger
from utils.config import REST_BASE_URL, CLASSROOM_ID, ACCOUNT_ID, ACCOUNT_ID2


# =========================================================
# 보조 함수
# =========================================================

def get_comment_info(board_api, article_id, target_comment_id, retry=5):
    """댓글 목록에서 특정 댓글을 찾아 반환"""
    target_str = str(target_comment_id)
    
    for attempt in range(retry):
        time.sleep(1) # 데이터 동기화 대기
        
        resp = board_api.get_comments(article_id, count=40)
        
        # 다양한 응답 구조 대응
        comments = []
        if isinstance(resp, list):
            comments = resp
        elif isinstance(resp, dict):
            comments = resp.get("article_comments") or \
                       resp.get("comments") or \
                       resp.get("data") or \
                       resp.get("results") or []
        
        for item in comments:
            c_id = item.get("id") or item.get("article_comment_id")
            if str(c_id) == target_str:
                return item
        
    return None


# =========================================================
# [Positive] 통합 시나리오 테스트
# =========================================================

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
        
        assert "_result" not in resp_create or resp_create.get("_result", {}).get("status") != "fail", \
            f"[BOARD_11] API 에러 발생: {resp_create}"
        
        article_id = resp_create.get("board_article_id")
        assert article_id is not None, f"[BOARD_11] 게시글 ID 없음: {resp_create}"
        logger.info(f"✅ [BOARD_11] 게시글 생성 성공: ID={article_id}")

        # =========================================================
        # Step 2: 게시글 조회 및 검증 (BOARD_12)
        # =========================================================
        logger.info("📝 Step 2: 게시글 조회 및 검증")
        time.sleep(0.5)
        created_info = board_api.get_article(article_id)
        
        assert created_info is not None, f"[BOARD_12] 게시글 조회 실패: ID={article_id}"
        assert created_info.get("title") == input_title, "[BOARD_12] 제목 불일치"
        logger.info("✅ 게시글 조회 및 데이터 검증 성공")

        # =========================================================
        # Step 3: 게시글 수정 (BOARD_13, BOARD_14)
        # =========================================================
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
        
        attachment_after = updated_info.get("article_attachment_count", 0)
        if attachment_after > attachment_before:
            logger.info(f"✅ [BOARD_14] 파일 첨부 성공")
        else:
            logger.warning(f"⚠️ [BOARD_14] 파일 첨부 갯수 변화 없음")

        # =========================================================
        # Step 4: 게시글 좋아요 (BOARD_06, BOARD_08)
        # =========================================================
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

        # =========================================================
        # Step 5: 목록 조회 및 검색 (BOARD_01~05)
        # =========================================================
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

        # =========================================================
        # Step 6: 댓글 CRUD (BOARD_16~20, BOARD_07, BOARD_09)
        # =========================================================
        logger.info("📝 Step 6: 댓글 CRUD")

        comment_content = "[Auto] 댓글 테스트"
        resp_cmt = board_api.create_comment(article_id, comment_content)
        comment_id = resp_cmt.get("article_comment_id")
        assert comment_id is not None, f"[BOARD_16] 댓글 생성 실패: {resp_cmt}"
        logger.info(f"✅ [BOARD_16] 댓글 생성 성공: ID={comment_id}")
        
        time.sleep(1) # 생성 대기
        
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


# =========================================================
# [Positive] 댓글 정렬 테스트 (BOARD_17, BOARD_18)
# =========================================================

def test_comment_sorting(client, board_api):
    """[TC] 댓글 정렬 검증"""
    logger.info("🚀 [Sorting TC] 댓글 정렬 테스트 시작")
    
    resp = board_api.create_article("[Sort] 정렬용", "내용", is_secret=False)
    temp_aid = resp.get("board_article_id")
    assert temp_aid, f"❌ 게시글 생성 실패: {resp}"
    logger.info(f"👉 테스트 게시글: ID={temp_aid}")

    created_ids = []
    
    try:
        # 댓글 3개 생성
        for i in range(1, 4):
            resp = board_api.create_comment(temp_aid, f"[Sort] 댓글 {i}")
            c_id = resp.get("article_comment_id")
            if c_id:
                created_ids.append(str(c_id))
                logger.info(f"   - 댓글 {i}: ID={c_id}")
            time.sleep(0.1) # 생성 순서 보장 (DB Timestamp)

        time.sleep(2) # 댓글 반영 대기

        # 1. 오래된 순 (id) -> order: asc
        logger.info("👉 오래된 순(ASC) 정렬 요청 (sort='id')")
        resp_list = board_api.get_comments(temp_aid, count=40, sort="id")
        
        comments = []
        if isinstance(resp_list, list):
            comments = resp_list
        elif isinstance(resp_list, dict):
            comments = resp_list.get("article_comments") or \
                       resp_list.get("comments") or \
                       resp_list.get("data") or \
                       resp_list.get("results") or []
                       
        server_ids = [str(c.get("id") or c.get("article_comment_id")) for c in comments]
        
        indices = [server_ids.index(cid) for cid in created_ids if cid in server_ids]
        if len(indices) == 3:
            assert indices == sorted(indices), f"❌ 오래된순 정렬 불일치 (실제: {indices})"
            logger.info("✅ [BOARD_17] 오래된순 정렬 성공")

        # 2. 최신 순 (-id) -> order: desc
        logger.info("👉 최신 순(DESC) 정렬 요청 (sort='-id')")
        resp_lat = board_api.get_comments(temp_aid, count=40, sort="-id")
        
        comments_lat = []
        if isinstance(resp_lat, list):
            comments_lat = resp_lat
        elif isinstance(resp_lat, dict):
            comments_lat = resp_lat.get("article_comments") or \
                           resp_lat.get("comments") or \
                           resp_lat.get("data") or \
                           resp_lat.get("results") or []

        server_ids_lat = [str(c.get("id") or c.get("article_comment_id")) for c in comments_lat]
        
        indices_lat = [server_ids_lat.index(cid) for cid in created_ids if cid in server_ids_lat]
        if len(indices_lat) == 3:
            assert indices_lat == sorted(indices_lat, reverse=True), f"❌ 최신순 정렬 불일치 (실제: {indices_lat})"
            logger.info("✅ [BOARD_18] 최신순 정렬 성공")

    finally:
        if temp_aid:
            board_api.delete_article(temp_aid)
            logger.info("🧹 정리 완료")


# =========================================================
# [Security] 타인 계정 사칭 (BOARD_29)
# =========================================================

def test_security_impersonation(board_api):
    """
    [Security TC] 타인 계정 사칭 글쓰기 시도 (Mass Assignment / IDOR)
    - 요청 바디에 타인의 ID를 강제로 넣어서 글을 써본다.
    - 확인 후 글은 자동 삭제 처리
    """
    logger.info("🚀 [Security] 타인 ID 사칭 글쓰기 테스트 시작")

    # 1. 공격 대상 설정 (타인 ID)
    if not ACCOUNT_ID2:
        logger.warning("⚠️ .env에 ACCOUNT_ID2가 설정되지 않아 테스트를 스킵합니다.")
        pytest.skip("ACCOUNT_ID2 not set")

    victim_id = ACCOUNT_ID2 
    logger.info(f"👉 내 ID: {ACCOUNT_ID}, 공격 대상(타인) ID: {victim_id}")

    # 2. 공격 페이로드 구성
    # 서버가 작성자를 식별할 때 쓸법한 필드명들에 타인 ID를 다 집어넣음
    payload = {
        "title": "[Security] 사칭 테스트",
        "content": f"이 글은 {ACCOUNT_ID}가 {victim_id} 명의로 작성을 시도한 글입니다.",
        "classroom_id": CLASSROOM_ID,
        "is_secret": "false",
        
        # [공격 벡터] ID 변조 시도
        "account_id": victim_id,
        "user_id": victim_id,
        "writer_id": victim_id,
        "created_by": victim_id,
        "author_id": victim_id,
        "user": {"id": victim_id}
    }

    # 3. 강제 POST 요청
    # BoardAPI의 _send_request를 직접 사용하여 조작된 payload 전송
    full_url = f"{REST_BASE_URL}{board_api.WRITE_PATH}/edit/"
    resp = board_api._send_request("POST", full_url, payload=payload)

    # 4. 결과 검증
    new_article_id = resp.get("board_article_id")
    
    # (1) 요청 자체가 거부되었으면 안전함 (Best case)
    if board_api.status_code >= 400:
        logger.info(f"✅ 서버가 요청을 거부함 (Status: {board_api.status_code}) - 안전함")
        return

    # (2) 글이 생성되었다면 작성자 확인
    if not new_article_id:
        logger.warning(f"⚠️ 글 생성 실패 또는 응답 구조 다름: {resp}")
        return

    try:
        time.sleep(1)
        created_article = board_api.get_article(new_article_id)
        
        # 작성자 ID 추출 (응답 구조에 따라 user.id 또는 created_by 등 확인)
        real_author_id = created_article.get("user", {}).get("id") or \
                         created_article.get("created_by")

        # (3) 판정
        if str(real_author_id) == str(victim_id):
            # 🚨 심각한 보안 취약점 발견
            pytest.fail(f"🚨 [CRITICAL] 사칭 성공! 내 토큰으로 {victim_id} 님의 글이 작성되었습니다.")
        
        elif str(real_author_id) == str(ACCOUNT_ID):
            # ✅ 입력한 ID는 무시되고, 내 토큰 주인 ID로 정상 등록됨 (안전)
            logger.info(f"✅ 사칭 실패: 입력한 ID({victim_id}) 무시됨. 내 ID({real_author_id})로 등록.")
        
        else:
            logger.warning(f"⚠️ 작성자 ID 확인 불가 (응답: {real_author_id})")

    finally:
        # 테스트용 데이터 정리
        if new_article_id:
            board_api.delete_article(new_article_id)
            logger.info("🧹 보안 테스트용 글 삭제 완료")
        # pass


# =========================================================
# [Negative] 제목 누락 테스트 (BOARD_12)
# =========================================================

def test_create_article_missing_title(client, board_api):
    logger.info("🚀 [BOARD_12] 제목 미입력 테스트")
    resp = board_api.create_article("", "내용")
    
    if board_api.status_code >= 400:
        logger.info(f"✅ 서버가 {board_api.status_code} 에러 반환")
    elif resp.get("_result", {}).get("status") == "fail":
        logger.info("✅ 응답 내 fail 상태 확인")
    else:
        logger.warning("⚠️ 서버가 빈 제목 허용함 (버그)")
        aid = resp.get("board_article_id")
        if aid:
            board_api.delete_article(aid)
    
    logger.info("✅ [BOARD_12] 테스트 완료")


# =========================================================
# [Negative] 필수 파라미터 누락 (BOARD_21, BOARD_22)
# =========================================================

def test_missing_required_params(client, board_api):
    logger.info("🚀 [Negative] 필수 파라미터 누락 테스트")

    logger.info("👉 [BOARD_21] skip 없이 요청")
    resp = board_api.get_list(skip=None, count=10)
    assert board_api.status_code == 422, f"❌ 기대: 422, 실제: {board_api.status_code}"
    logger.info("✅ [BOARD_21] 통과")

    logger.info("👉 [BOARD_22] count 없이 요청")
    resp = board_api.get_list(skip=0, count=None)
    assert board_api.status_code == 422, f"❌ 기대: 422, 실제: {board_api.status_code}"
    logger.info("✅ [BOARD_22] 통과")


# =========================================================
# [Negative] SQL Injection 방어 (BOARD_23)
# =========================================================

def test_security_sql_injection(client, board_api):
    logger.info("🚀 [BOARD_23] SQL Injection 방어 테스트")
    
    payload = "' OR '1'='1"
    resp = board_api.get_list(filter_title=payload, skip=0, count=20)
    
    if board_api.status_code == 200:
        articles = resp if isinstance(resp, list) else []
        assert len(articles) == 0, f"❌ 데이터 노출: {len(articles)}건"
        logger.info("✅ 검색 결과 0건 (방어 성공)")
    elif board_api.status_code == 400:
        logger.info("✅ 400 에러 (방어 성공)")
    else:
        pytest.fail(f"❌ 예상치 못한 응답: {board_api.status_code}")


# =========================================================
# [Negative] 헤더 검증 (BOARD_24, BOARD_27)
# =========================================================

def test_header_validation(client, board_api):
    logger.info("🚀 [BOARD_24/27] 헤더 검증 테스트")

    logger.info("👉 [BOARD_24] 정상 헤더")
    resp = board_api.get_list(skip=0, count=10)
    assert board_api.status_code == 200, f"❌ 정상 요청 실패: {board_api.status_code}"
    logger.info("✅ [BOARD_24] 성공")

    logger.info("👉 [BOARD_27] 조작된 헤더")
    resp = board_api.get_list(skip=0, count=10, headers={"x-elice-org-name-short": "hacker"})
    assert board_api.status_code in [400, 403, 404, 409], f"❌ 차단 안됨: {board_api.status_code}"
    logger.info(f"✅ [BOARD_27] 차단 확인 ({board_api.status_code})")


# =========================================================
# [Negative] 권한 검증 (BOARD_25)
# =========================================================

def test_permission_check(client, board_api):
    logger.info("🚀 [BOARD_25] 타인 게시글 삭제 권한 테스트")
    
    other_id = 67448
    resp = board_api.delete_article(other_id)
    
    # 응답 body에서 에러 확인
    if isinstance(resp, dict) and resp.get("_result", {}).get("status") == "fail":
        logger.info(f"✅ 삭제 거부됨 (fail_code: {resp.get('fail_code')})")
        return
    
    if board_api.status_code == 403:
        logger.info("✅ 403 Forbidden")
    elif board_api.status_code == 200:
        time.sleep(1)
        check = board_api.get_article(other_id)
        if check is None:
            pytest.fail("❌ 타인 게시글 삭제됨! (보안 취약점)")
        else:
            logger.warning("⚠️ 200이지만 실제 삭제 안됨")
    elif board_api.status_code == 404:
        logger.warning("⚠️ 게시글 없음 (404)")
    else:
        logger.info(f"✅ 삭제 실패 ({board_api.status_code})")


# =========================================================
# [Negative] 댓글 내용 미입력 (BOARD_28)
# =========================================================

def test_create_comment_missing_content(client, board_api):
    logger.info("🚀 [BOARD_28] 댓글 내용 미입력 테스트")
    
    resp = board_api.create_article("[Test] 댓글용", "내용", is_secret=False)
    temp_aid = resp.get("board_article_id")
    
    if not temp_aid:
        pytest.skip(f"게시글 생성 실패: {resp}")
    
    try:
        resp_cmt = board_api.create_comment(temp_aid, "")
        
        if board_api.status_code >= 400:
            logger.info(f"✅ {board_api.status_code} 에러 반환")
        elif resp_cmt.get("_result", {}).get("status") == "fail":
            logger.info("✅ fail 상태 확인")
        else:
            logger.warning("⚠️ 빈 댓글 허용됨 (버그)")
            cid = resp_cmt.get("article_comment_id")
            if cid:
                board_api.delete_comment(cid, temp_aid)
    finally:
        if temp_aid:
            board_api.delete_article(temp_aid)
    
    logger.info("✅ [BOARD_28] 테스트 완료")

# =========================================================
# [Security] 특정 게시글(67606)에 타인 계정 댓글 사칭 시도 (BOARD_30)
# =========================================================

def test_security_comment_impersonation_fixed_article(board_api):
    """
    [Security TC] 지정된 게시글(ID: 67606)에 타인 ID로 댓글 작성 시도
    """
    from utils.config import ACCOUNT_ID, ACCOUNT_ID2, REST_BASE_URL, CLASSROOM_ID
    import time

    # 1. 테스트 대상 설정
    target_article_id = 67606  # 사용자가 지정한 게시글 ID
    
    if not ACCOUNT_ID2:
        pytest.skip("ACCOUNT_ID2(타인 ID)가 설정되지 않아 테스트를 건너뜁니다.")

    victim_id = ACCOUNT_ID2
    logger.info(f"🚀 [Security] 게시글 {target_article_id}번에 타인({victim_id}) 명의 댓글 작성 시도")

    comment_id = None

    try:
        # 2. 공격 페이로드 구성 (Body에 타인 ID 주입)
        payload = {
            "board_article_id": target_article_id,
            "content": f"[Security] {ACCOUNT_ID}가 {victim_id} 님인 척 작성한 댓글입니다.",
            "classroom_id": CLASSROOM_ID,
            "is_secret": "false",
            
            # [공격 포인트] 작성자 ID 변조 시도
            "account_id": victim_id,
            "user_id": victim_id,
            "writer_id": victim_id,
            "created_by": victim_id,
            "author_id": victim_id,
            "user": {"id": victim_id}
        }

        # 3. 강제 POST 요청 보내기
        url = f"{REST_BASE_URL}{board_api.WRITE_PATH}/comment/edit/"
        resp = board_api._send_request("POST", url, payload=payload)

        # 4. 결과 검증
        if board_api.status_code >= 400:
            logger.info(f"✅ 서버가 요청을 거부함 (Status: {board_api.status_code}) - 안전함")
            return

        comment_id = resp.get("article_comment_id")
        if not comment_id:
            logger.warning(f"⚠️ 댓글 생성 실패 또는 응답 구조 다름: {resp}")
            return
        
        logger.info(f"👉 댓글이 생성되었습니다! ID: {comment_id}")

        # 5. 생성된 댓글의 '진짜 작성자' 확인
        time.sleep(1) # 서버 반영 대기
        
        # 댓글 조회 (단건 조회 API가 없으므로 목록에서 찾기)
        # 최신순 정렬(-id)로 가져오면 방금 쓴 게 맨 위에 있을 확률이 높음
        resp_list = board_api.get_comments(target_article_id, count=10, sort="-id")
        
        comments = []
        if isinstance(resp_list, list):
            comments = resp_list
        elif isinstance(resp_list, dict):
            comments = resp_list.get("article_comments") or \
                       resp_list.get("comments") or \
                       resp_list.get("data") or \
                       resp_list.get("results") or []

        # 내 댓글 찾기
        target_comment = None
        for c in comments:
            cid = str(c.get("id") or c.get("article_comment_id"))
            if cid == str(comment_id):
                target_comment = c
                break
        
        if not target_comment:
            logger.warning(f"⚠️ 목록에서 방금 쓴 댓글({comment_id})을 찾을 수 없습니다.")
            return

        # 작성자 ID 추출
        real_author_id = target_comment.get("user", {}).get("id") or \
                         target_comment.get("created_by")
        
        logger.info(f"🕵️‍♂️ 실제 작성자: {real_author_id} / 공격 대상: {victim_id}")

        # 6. 최종 판정
        if str(real_author_id) == str(victim_id):
            pytest.fail(f"🚨 [CRITICAL] 사칭 성공! {victim_id} 님의 이름으로 댓글이 등록되었습니다.")
        elif str(real_author_id) == str(ACCOUNT_ID):
            logger.info("✅ 사칭 실패: 입력한 ID는 무시되고 '내 ID'로 정상 등록됨.")
        else:
            logger.warning(f"⚠️ 작성자 ID 확인 불가: {real_author_id}")

    finally:
        # 🧹 뒷정리: 게시글은 남기고, '테스트용 댓글'만 삭제합니다.
        if comment_id:
            board_api.delete_comment(comment_id, target_article_id)
            logger.info(f"🧹 테스트용 댓글({comment_id}) 삭제 완료")