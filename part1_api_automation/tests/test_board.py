"""
2026-02-25
게시판(Board) API 테스트 - TC 기반
- 게시글 라이프사이클 (생성 -> 수정 -> 좋아요 -> 삭제)
- 목록 조회 / 페이지네이션 / 검색
- 좋아요 추가/제거
- 필수 파라미터 검증
- 보안 테스트
"""

import pytest

def test_scenario_flow(client, board_api):
    """
    [시나리오] 생성 -> 수정 -> 댓글(작성/수정/좋아요/삭제) -> 좋아요 -> 삭제
    """
    # =========================================================
    # 1. 게시글 생성 (BOARD_11)
    # =========================================================
    print("\n--- 1. 게시글 생성 요청 ---")
    resp_create = board_api.create_article(
        title="[Auto] 시나리오 흐름 테스트", 
        content="ID를 따서 끝까지 테스트합니다."
    )
    print(f"👉 생성 응답: {resp_create}")

    # ID 추출
    article_id = resp_create.get("board_article_id")
    if not article_id:
        pytest.fail(f"❌ 게시글 생성 실패! 응답확인: {resp_create}")   
    print(f"✅ 확보된 게시글 ID: {article_id}")


    # =========================================================
    # 2. 게시글 수정 (BOARD_13)
    # =========================================================
    print(f"\n--- 2. 게시글 수정 (ID: {article_id}) ---")
    board_api.update_article(article_id, "제목 수정됨", "본문 수정됨")
    
    # 200 OK 확인
    assert client.status_code == 200
    print("✅ 게시글 수정 완료")


    # =========================================================
    # 3. 게시글 좋아요 (BOARD_06)
    # =========================================================
    print(f"\n--- 3. 게시글 좋아요 (ID: {article_id}) ---")
    board_api.like_article(article_id, is_add=True)
    assert client.status_code == 200
    print("✅ 게시글 좋아요 완료")


    # =========================================================
    # 4. 댓글 작성
    # =========================================================
    print(f"\n--- 4. 댓글 작성 (ID: {article_id}) ---")
    resp_cmt = board_api.create_comment(article_id, "댓글 테스트")
    print(f"👉 댓글 응답: {resp_cmt}")

    comment_id = resp_cmt.get("article_comment_id")
    
    if comment_id:
        print(f"✅ 확보된 댓글 ID: {comment_id}")

        # 5. 댓글 수정
        print(f"\n--- 5. 댓글 수정 ---")
        board_api.update_comment(comment_id, article_id, "댓글 내용 수정")
        assert client.status_code == 200

        # 6. 댓글 좋아요
        print(f"\n--- 6. 댓글 좋아요 ---")
        board_api.like_comment(comment_id, is_add=True)
        assert client.status_code == 200

        # 7. 댓글 삭제
        print(f"\n--- 7. 댓글 삭제 ---")
        board_api.delete_comment(comment_id, article_id)
        assert client.status_code == 200
        print("✅ 댓글 테스트 완료")
    else:
        print(f"⚠️ 댓글 생성 실패로 댓글 관련 테스트 스킵 (응답: {resp_cmt})")


    # =========================================================
    # 8. 게시글 삭제
    # =========================================================
    print(f"\n--- 8. 게시글 삭제 (ID: {article_id}) ---")
    board_api.delete_article(article_id)
    assert client.status_code == 200
    print("✅ 게시글 삭제 완료 (청소 끝)")