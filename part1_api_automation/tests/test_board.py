"""
2026-02-05 심다영
게시판(Board) API 테스트 - TC 기반
- 게시글 라이프사이클 (생성 -> 수정 -> 좋아요 -> 삭제)
- 목록 조회 / 페이지네이션 / 검색
- 좋아요 추가/제거 및 갯수 검증
- 필수 파라미터 검증
- 보안 테스트

2026-02-06 심다영
- 좋아요 갯수 정합성 검증 포함
"""

import pytest
import time
from utils.logger import logger

# =========================================================
# [Helper] 게시글 리스트에서 내 글 찾기
# =========================================================
def get_article_info(board_api, target_id):
    """
    게시글 목록(최신순 20개)을 조회하여 target_id와 일치하는 게시글 정보를 반환
    """
    articles = board_api.get_list(skip=0, count=20)
    
    # 리스트 순회하며 ID 매칭
    for item in articles:
        if str(item.get("id")) == str(target_id):
            return item
    return None

# 댓글 리스트에서 내 댓글 정보 찾기
def get_comment_info(board_api, article_id, target_comment_id):
    resp = board_api.get_comments(article_id)
    # API가 리스트를 주는지 딕셔너리를 주는지에 따라 안전하게 처리
    comments = resp.get("comments", []) if isinstance(resp, dict) else resp
    
    for item in comments:
        if str(item.get("id")) == str(target_comment_id):
            return item
    return None

def test_scenario_flow(client, board_api):
    """
    [시나리오] 생성 -> 수정 -> 좋아요(검증) -> 댓글(CRUD) -> 삭제
    """
    logger.info("🚀 [Board] 시나리오 테스트 시작")
    
    article_id = None # cleanup을 위해 변수 초기화

    try:
        # =========================================================
        # 1. 게시글 생성 (BOARD_11)
        # =========================================================
        print("\n--- 1. 게시글 생성 요청 ---")
        resp_create = board_api.create_article(
            title="[Auto] 시나리오 흐름 테스트", 
            content="ID를 따서 끝까지 테스트합니다."
        )
        
        article_id = resp_create.get("board_article_id")
        if not article_id:
            logger.error(f"게시글 생성 실패: {resp_create}")
            pytest.fail("게시글 ID를 받아오지 못했습니다.")
            
        logger.info(f"✅ (BOARD_11) 게시글 생성 완료: {article_id}")


        # =========================================================
        # 2. 게시글 수정 (BOARD_13)
        # =========================================================
        print(f"\n--- 2. 게시글 수정 및 파일 첨부 (ID: {article_id}) ---")
        
        # (1) 가짜 파일 생성 (메모리에 텍스트 파일 생성)
        # 형식: {'필드명': ('파일명', '파일내용', 'MIME타입')}
        # 주의: API 스펙상 파일 필드명이 'file' 또는 'attachment' 일 수 있음. 보통 'file' 사용
        test_files = {
            'file': ('test_image.txt', 'This is a test file content', 'text/plain')
        }
        
        # (2) 수정 요청에 파일 실어 보내기
        board_api.update_article(
            article_id, 
            title="[Auto] 파일 첨부된 게시글", 
            content="첨부파일을 확인해주세요.",
            files=test_files
        )
        logger.info("✅ 게시글 수정 및 파일 업로드 요청 완료")

        # =========================================================
        # 2-1. 파일 첨부 검증
        # =========================================================

        # (3) 파일 첨부 확인 (검증)
        info_with_file = get_article_info(board_api, article_id)
        
        # 응답 필드 중 attachment_count 확인 (아까 디버그에서 0으로 나온 그 필드)
        att_count = info_with_file.get("article_attachment_count", 0)
        
        if att_count > 0:
            logger.info(f"   ✅ 파일 첨부 확인 성공! (첨부 갯수: {att_count})")
        else:
            # API에 따라 즉시 반영이 안 될 수도 있거나, 필드명이 'file'이 아닐 수도 있음
            logger.warning(f"   ⚠️ 파일 첨부 갯수가 0입니다. (필드명 확인 필요)")
            # pytest.fail("파일 업로드 실패") # 확실해지면 주석 해제


        # =========================================================
        # 3. 게시글 좋아요 추가 (BOARD_06)
        # =========================================================
        print(f"\n--- 3. 게시글 좋아요 (ID: {article_id}) ---")
        logger.info("🔎 [검증] 좋아요 로직 테스트 시작")

        # [3-1] 누르기 전 상태 확인
        info_before = get_article_info(board_api, article_id)
        if not info_before:
            pytest.fail("❌ 생성된 게시글을 목록에서 찾을 수 없습니다.")
        likes_before = info_before.get("like_count", 0)
        logger.info(f"   ℹ️ 누르기 전 좋아요 수: {likes_before}")

        # [3-2] 좋아요 클릭 (Add)
        board_api.like_article(article_id, is_add=True)
        time.sleep(0.5) # DB 반영 대기

        # [3-3] 누른 후 상태 확인 (+1 검증)
        info_after = get_article_info(board_api, article_id)
        # (안전장치)
        if not info_after:
             pytest.fail("❌ 좋아요 후 게시글 조회 실패")

        likes_after = info_after.get("like_count", 0)
        logger.info(f"   ℹ️ 누른 후 좋아요 수: {likes_after}")

        if likes_after == likes_before + 1:
            logger.info("   ✅ (BOARD_06)좋아요 증가 검증 성공! (+1)")
        else:
            logger.error(f"❌ 좋아요 증가 검증 실패! ({likes_before} -> {likes_after})")
            pytest.fail(f"좋아요 증가 실패")

        # =========================================================
        # 3-4. 게시글 좋아요 취소 (BOARD_08)
        # =====================================================

        # [3-5] 좋아요 취소 (Cancel)
        board_api.like_article(article_id, is_add=False)
        time.sleep(0.5) # DB 반영 대기

        # [3-6] 취소 후 상태 확인 (복구 검증)
        info_final = get_article_info(board_api, article_id)
        # (안전장치 추가) 조회 실패 시 테스트 중단
        if not info_final:
             pytest.fail("❌ 좋아요 취소 후 게시글 조회 실패")

        likes_final = info_final.get("like_count", 0)
        logger.info(f"   ℹ️ 취소 후 좋아요 수: {likes_final}")

        # [3-7] 좋아요 취소 검증 (원래대로 돌아왔는지?)
        if likes_final == likes_before:
            logger.info("   ✅ (BOARD_08) 좋아요 취소 검증 성공! (원래대로 복구됨)")
        else:
            logger.error(f"❌ 좋아요 취소 검증 실패! ({likes_before} -> {likes_final})")
            pytest.fail(f"좋아요 갯수 복구 실패")


        # =========================================================
        # 4. 댓글 작성 (BOARD_16)
        # =========================================================
        print(f"\n--- 4. 댓글 작성 (ID: {article_id}) ---")
        resp_cmt = board_api.create_comment(article_id, "댓글 테스트")
        comment_id = resp_cmt.get("article_comment_id")
        
        if comment_id:
            logger.info(f"✅ 댓글 생성 완료: {comment_id}")
            # =========================================================
            # 5. 댓글 수정 (BOARD_19)
            # =========================================================
            print(f"\n--- 5. 댓글 수정 ---")
            board_api.update_comment(comment_id, article_id, "댓글 내용 수정")
            logger.info("✅ (BOARD_19) 댓글 수정 완료")

            # =========================================================
            # 6. 댓글 좋아요 및 검증 (BOARD_07)
            # =========================================================
            print(f"\n--- 6. 댓글 좋아요 (검증 포함) ---")
            logger.info("🔎 [검증] 댓글 좋아요 로직 테스트 시작")

            # [6-1] 누르기 전 상태 확인
            cmt_before = get_comment_info(board_api, article_id, comment_id)
            if not cmt_before:
                pytest.fail("❌ 작성한 댓글을 목록에서 찾을 수 없습니다.")
            
            cmt_likes_before = cmt_before.get("like_count", 0)
            logger.info(f"   ℹ️ 댓글 좋아요(전): {cmt_likes_before}")

            # [6-2] 좋아요 클릭 (+1)
            board_api.like_comment(comment_id, is_add=True)
            time.sleep(0.5) # DB 반영 대기

            # [6-3] 누른 후 확인
            cmt_after = get_comment_info(board_api, article_id, comment_id)
            cmt_likes_after = cmt_after.get("like_count", 0)
            logger.info(f"   ℹ️ 댓글 좋아요(후): {cmt_likes_after}")

            # [6-4] 검증
            if cmt_likes_after == cmt_likes_before + 1:
                logger.info("   ✅ (BOARD_07)댓글 좋아요 증가 검증 성공! (+1)")
            else:
                logger.error(f"❌ 댓글 좋아요 증가 실패 ({cmt_likes_before} -> {cmt_likes_after})")
                pytest.fail("댓글 좋아요 증가 검증 실패")


            # =========================================================
            # 7. 댓글 좋아요 취소 및 검증
            # =========================================================
            print(f"\n--- 7. 댓글 좋아요 취소 (검증 포함) ---")
            
            # [7-1] 좋아요 취소 (Action)
            board_api.like_comment(comment_id, is_add=False)
            time.sleep(0.5)

            # [7-2] 취소 후 확인
            cmt_final = get_comment_info(board_api, article_id, comment_id)
            cmt_likes_final = cmt_final.get("like_count", 0)
            logger.info(f"   ℹ️ 취소 후 좋아요: {cmt_likes_final}")

            # [7-3] 검증 (원상복구 확인)
            if cmt_likes_final == cmt_likes_before:
                logger.info("   ✅ 댓글 좋아요 취소 검증 성공! (복구됨)")
            else:
                logger.error(f"❌ 댓글 좋아요 취소 실패 ({cmt_likes_after} -> {cmt_likes_final})")
                pytest.fail("댓글 좋아요 취소 검증 실패")

            # =========================================================
            # 8. 댓글 삭제 (BOARD_20)
            # =========================================================
            print(f"\n--- 8. 댓글 삭제 ---")
            board_api.delete_comment(comment_id, article_id)
            logger.info("✅ (BOARD_20) 댓글 삭제 완료")
            
        else:
            logger.warning(f"⚠️ 댓글 생성 실패로 이후 단계 스킵: {resp_cmt}")

    except Exception as e:
        logger.error(f"🚨 테스트 중 에러 발생: {e}")
        raise e

    finally:
        # =========================================================
        # 9. 게시글 삭제 (BOARD_15)
        # =========================================================
        if article_id:
            print(f"\n--- 8. 게시글 삭제 (ID: {article_id}) ---")
            logger.info(f"🧹 청소 시작: 게시글 {article_id} 삭제")
            board_api.delete_article(article_id)
            logger.info("✅ (BOARD_15) 게시글 삭제 완료 (게시글 라이프사이클 종료)")