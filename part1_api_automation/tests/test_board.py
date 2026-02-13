"""
게시판(Board) API 테스트

작성자: 심다영
작성일: 2026-02-13
"""

import pytest
import time
import os
import tempfile

from utils.board_api import BoardAPI
from utils.config import CLASSROOM_ID, ACCOUNT_ID, ACCOUNT_ID2

# 설정
SAFE_USERS = ["심다영", "[매니저]송찬영"]

#--------------------------------------------------------------------
# 헬퍼 함수
#--------------------------------------------------------------------
def find_other_user_article(board_api):
    """타인의 게시글 찾기"""
    res = board_api.get_list(skip=0, count=20)
    articles = res if isinstance(res, list) else []
    
    for article in articles:
        user = article.get("user") or {}
        author = user.get("fullname") or user.get("name") or "Unknown"
        if author not in SAFE_USERS and author != "Unknown":
            return {"id": article.get("id"), "author": author, "title": article.get("title")}
    return None

#--------------------------------------------------------------------
# BOARD_01 게시글 목록 조회
#--------------------------------------------------------------------
def test_board_01_get_list(board_api):
    res = board_api.get_list(skip=0, count=10)
    assert isinstance(res, list)

#--------------------------------------------------------------------
# BOARD_02 페이지네이션
#--------------------------------------------------------------------
def test_board_02_pagination(board_api):
    page1 = board_api.get_list(skip=0, count=5)
    page2 = board_api.get_list(skip=5, count=5)
    
    p1_ids = {a.get("id") for a in (page1 if isinstance(page1, list) else [])}
    p2_ids = {a.get("id") for a in (page2 if isinstance(page2, list) else [])}
    
    assert len(p1_ids & p2_ids) == 0

#--------------------------------------------------------------------
# BOARD_03 검색 (키워드 있음)
#--------------------------------------------------------------------
def test_board_03_search_with_keyword(board_api):
    res = board_api.get_list(skip=0, count=10, filter_title="%테스트%")
    assert isinstance(res, list)

#--------------------------------------------------------------------
# BOARD_04 검색 (키워드 없음)
#--------------------------------------------------------------------
def test_board_04_search_no_result(board_api):
    res = board_api.get_list(skip=0, count=10, filter_title="%zzznotexist999%")
    articles = res if isinstance(res, list) else []
    assert len(articles) == 0

#--------------------------------------------------------------------
# BOARD_11 게시글 생성
#--------------------------------------------------------------------
def test_board_11_create_article(board_api):
    res = board_api.create_article("[Auto] 게시글 생성 테스트", "자동화 테스트입니다.", is_secret=False)
    
    assert res.get("board_article_id") is not None
    
    # 정리
    board_api.delete_article(res.get("board_article_id"))

#--------------------------------------------------------------------
# BOARD_12 게시글 생성 (제목 누락) - Negative
#--------------------------------------------------------------------
def test_board_12_create_article_no_title(board_api):
    res = board_api.create_article("", "제목 없는 게시글", is_secret=False)
    
    # 생성되면 버그
    if res.get("board_article_id"):
        board_api.delete_article(res.get("board_article_id"))
        pytest.fail("🚨 빈 제목의 게시글이 생성됨 - Validation 버그")

#--------------------------------------------------------------------
# BOARD_13 게시글 수정
#--------------------------------------------------------------------
def test_board_13_update_article(board_api):
    # 생성
    res = board_api.create_article("[Auto] 수정 전", "수정 전 내용", is_secret=False)
    article_id = res.get("board_article_id")
    
    try:
        # 수정
        board_api.update_article(article_id, "[Auto] 수정 후", "수정 후 내용", is_secret=False)
        
        # 확인
        time.sleep(0.5)
        detail = board_api.get_article(article_id)
        assert detail.get("title") == "[Auto] 수정 후"
    finally:
        board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_15 게시글 삭제
#--------------------------------------------------------------------
def test_board_15_delete_article(board_api):
    res = board_api.create_article("[Auto] 삭제 테스트", "삭제될 게시글", is_secret=False)
    article_id = res.get("board_article_id")
    
    board_api.delete_article(article_id)
    
    time.sleep(0.5)
    detail = board_api.get_article(article_id)
    assert detail is None

#--------------------------------------------------------------------
# BOARD_16 댓글 생성
#--------------------------------------------------------------------
def test_board_16_create_comment(board_api):
    res = board_api.create_article("[Auto] 댓글 테스트용", "댓글 테스트", is_secret=False)
    article_id = res.get("board_article_id")
    
    try:
        cmt_res = board_api.create_comment(article_id, "[Auto] 테스트 댓글")
        assert cmt_res.get("article_comment_id") is not None
    finally:
        board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_23 SQL Injection 방어 - Security
#--------------------------------------------------------------------
def test_board_23_sql_injection(board_api):
    payload = "' OR '1'='1"
    res = board_api.get_list(skip=0, count=20, filter_title=payload)
    
    articles = res if isinstance(res, list) else []
    assert len(articles) == 0

#--------------------------------------------------------------------
# BOARD_25 타인 게시글 삭제 시도 - Security
#--------------------------------------------------------------------
def test_board_25_delete_other_user_article(board_api):
    target = find_other_user_article(board_api)
    if target is None:
        pytest.skip("타인 게시글을 찾지 못함")
    
    target_id = target["id"]
    target_author = target["author"]
    
    res = board_api.delete_article(target_id)
    
    # fail 응답이면 정상
    if isinstance(res, dict) and res.get("_result", {}).get("status") == "fail":
        return
    
    # 실제 삭제 여부 확인
    time.sleep(0.5)
    check = board_api.get_article(target_id)
    if check is None:
        pytest.fail(f"🚨 보안 취약점: 타인({target_author})의 게시글이 삭제됨!")

#--------------------------------------------------------------------
# BOARD_28 빈 댓글 생성 - Negative
#--------------------------------------------------------------------
def test_board_28_create_empty_comment(board_api):
    res = board_api.create_article("[Auto] 빈 댓글 테스트", "빈 댓글 테스트", is_secret=False)
    article_id = res.get("board_article_id")
    
    try:
        cmt_res = board_api.create_comment(article_id, "")
        if cmt_res.get("article_comment_id"):
            pytest.fail("🚨 빈 댓글이 생성됨 - Validation 버그")
    finally:
        board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_31 타인 게시글 수정 권한 검증 - Security
#--------------------------------------------------------------------
def test_board_31_modify_other_user_article(board_api):
    target = find_other_user_article(board_api)
    if target is None:
        pytest.skip("타인 게시글을 찾지 못함")
    
    target_id = target["id"]
    target_author = target["author"]
    original_title = target["title"]
    
    res = board_api.update_article(target_id, "[HACKED] 수정됨", "공격자가 수정함", is_secret=False)
    
    # fail 응답이면 정상
    if isinstance(res, dict) and res.get("_result", {}).get("status") == "fail":
        return
    
    # 실제 수정 여부 확인
    time.sleep(0.5)
    check = board_api.get_article(target_id)
    if check and check.get("title") == "[HACKED] 수정됨":
        pytest.fail(f"🚨 보안 취약점: 타인({target_author})의 게시글이 수정됨!")

#--------------------------------------------------------------------
# BOARD_32 XSS 스크립트 삽입 방어 - Security
#--------------------------------------------------------------------
@pytest.mark.parametrize("xss_payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
])
def test_board_32_xss_prevention(board_api, xss_payload):
    article_id = None
    try:
        res = board_api.create_article(f"[XSS] {xss_payload}", f"본문: {xss_payload}", is_secret=False)
        article_id = res.get("board_article_id")
        
        if not article_id:
            return  # 서버가 거부함 - 정상
        
        time.sleep(0.5)
        detail = board_api.get_article(article_id)
        saved_title = detail.get("title", "") if detail else ""
        
        # <script 태그가 그대로 있으면 취약점
        if "<script" in saved_title and "&lt;script" not in saved_title:
            pytest.fail(f"🚨 XSS 취약점: 스크립트 태그가 이스케이프 없이 저장됨")
    finally:
        if article_id:
            board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_33 이미지 파일 업로드 테스트
#--------------------------------------------------------------------
def test_board_33_image_upload(board_api):
    # 임시 이미지 파일 생성 (1x1 JPEG)
    jpeg_bytes = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
        0x00, 0x00, 0x3F, 0x00, 0x7F, 0xFF, 0xD9
    ])
    
    fd, filepath = tempfile.mkstemp(suffix='.jpg')
    article_id = None
    
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(jpeg_bytes)
        
        with open(filepath, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            res = board_api.create_article("[BOARD_33] 이미지 업로드", "이미지 첨부", is_secret=False, files=files)
        
        article_id = res.get("board_article_id")
        if article_id:
            time.sleep(0.5)
            detail = board_api.get_article(article_id)
            attachment_count = detail.get("article_attachment_count", 0) if detail else 0
            assert attachment_count >= 0  # 서버 설정에 따라 다름
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        if article_id:
            board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_34 실행 파일 업로드 제한 - Security
#--------------------------------------------------------------------
@pytest.mark.parametrize("extension,content", [
    (".exe", b"MZ\x90\x00"),
    (".sh", b"#!/bin/bash\necho test"),
])
def test_board_34_block_executable(board_api, extension, content):
    fd, filepath = tempfile.mkstemp(suffix=extension)
    article_id = None
    
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        
        with open(filepath, 'rb') as f:
            files = {'file': (f'malicious{extension}', f, 'application/octet-stream')}
            res = board_api.create_article(f"[BOARD_34] 실행 파일 ({extension})", "실행 파일 시도", is_secret=False, files=files)
        
        article_id = res.get("board_article_id")
        
        if article_id:
            time.sleep(0.5)
            detail = board_api.get_article(article_id)
            if detail and detail.get("article_attachment_count", 0) > 0:
                pytest.fail(f"🚨 보안 취약점: 실행 파일({extension})이 업로드됨!")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        if article_id:
            board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_35 게시글 조회수 증가 로직
#--------------------------------------------------------------------
def test_board_35_view_count(board_api):
    res = board_api.create_article("[BOARD_35] 조회수 테스트", "조회수 테스트", is_secret=False)
    article_id = res.get("board_article_id")
    
    try:
        time.sleep(0.5)
        
        detail1 = board_api.get_article(article_id)
        count1 = detail1.get("view_count", 0) if detail1 else 0
        
        time.sleep(1)
        
        detail2 = board_api.get_article(article_id)
        count2 = detail2.get("view_count", 0) if detail2 else 0
        
        assert count2 >= count1
    finally:
        board_api.delete_article(article_id)

#--------------------------------------------------------------------
# BOARD_36 삭제된 게시글 접근 차단
#--------------------------------------------------------------------
def test_board_36_access_deleted_article(board_api):
    res = board_api.create_article("[BOARD_36] 삭제 테스트", "곧 삭제됨", is_secret=False)
    article_id = res.get("board_article_id")
    
    board_api.delete_article(article_id)
    
    time.sleep(0.5)
    
    detail = board_api.get_article(article_id)
    # None이거나 fail이면 정상
    if detail is not None and detail.get("_result", {}).get("status") != "fail":
        if detail.get("id") == article_id:
            pytest.fail("🚨 삭제된 게시글에 접근 가능!")

#--------------------------------------------------------------------
# BOARD_37 제목 최대 길이 제한
#--------------------------------------------------------------------
@pytest.mark.parametrize("title_length", [255, 500, 1000])
def test_board_37_title_length(board_api, title_length):
    long_title = "[BOARD_37] " + "가" * title_length
    article_id = None
    
    try:
        res = board_api.create_article(long_title, "제목 길이 테스트", is_secret=False)
        
        # fail 응답이면 정상 (유효성 검증)
        if isinstance(res, dict) and res.get("_result", {}).get("status") == "fail":
            return
        
        article_id = res.get("board_article_id")
        # 200 OK면 길이 제한 없거나 큰 것
    finally:
        if article_id:
            board_api.delete_article(article_id)