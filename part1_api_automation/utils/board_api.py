"""
2026-02-05 심다영
게시판(Board) API 유틸리티 클래스
- 게시글 생성, 조회, 수정, 삭제, 좋아요 기능 포함

2026-02-06 심다영
- 파일 첨부 기능 추가 (Multipart 전송)
- get_comments() 함수 추가
- 하드코딩 제거 → config.py에서 상수 import
"""

from utils.config import config, CLASSROOM_ID, ORG_NAME

# config에서 Base URL 가져오기
REST_BASE_URL = config["rest_base_url"]
CLASSROOM_BASE_URL = config["classroom_base_url"]


class BoardAPI:
    """게시판 API 래퍼 클래스"""
    
    WRITE_PATH = "/org/qatrack/board/article"

    def __init__(self, client):
        self.client = client
        self.client.session.headers.update({
            "x-elice-org-name-short": ORG_NAME
        })

    def _send_request(self, method, url, payload=None, params=None, extra_headers=None, files=None):
        """
        공통 요청 메서드
        - Multipart 전송 지원 (파일 첨부)
        
        Args:
            method: HTTP 메서드 (GET, POST)
            url: 요청 URL
            payload: 텍스트 데이터 (dict)
            params: 쿼리 파라미터 (dict)
            extra_headers: 추가 헤더 (dict)
            files: 파일 데이터 (dict) - {'file': ('filename', content, 'mime_type')}
        
        Returns:
            dict or str: 응답 데이터
        """
        headers = dict(self.client.session.headers)
        headers["Content-Type"] = None  # Multipart 자동 설정
            
        if extra_headers:
            headers.update(extra_headers)

        # Multipart 데이터 조립
        multi_part_data = {}
        
        # 1. 일반 텍스트 데이터
        if payload:
            for key, value in payload.items():
                multi_part_data[key] = (None, str(value))
        
        # 2. 파일 데이터 병합
        if files:
            multi_part_data.update(files)

        if method == "POST":
            response = self.client.session.post(url, files=multi_part_data, headers=headers)
        else:
            response = self.client.session.get(url, params=params, headers=headers)
            
        self.client.status_code = response.status_code
        try:
            return response.json()
        except:
            return response.text

    # =========================================================
    # 게시글 CRUD
    # =========================================================

    def create_article(self, title, content, is_secret=True, files=None):
        """
        게시글 생성 (BOARD_11)
        
        Args:
            title: 제목
            content: 내용
            is_secret: 비밀글 여부 (기본 True)
            files: 첨부파일 (선택)
        
        Returns:
            dict: 생성 결과 (board_article_id 포함)
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "title": title,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    def update_article(self, article_id, title, content, is_secret=True, files=None):
        """
        게시글 수정 (BOARD_13, BOARD_14)
        
        Args:
            article_id: 수정할 게시글 ID
            title: 제목
            content: 내용
            is_secret: 비밀글 여부
            files: 첨부파일 (선택)
        
        Returns:
            dict: 수정 결과
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "board_article_id": article_id,
            "title": title,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    def delete_article(self, article_id):
        """
        게시글 삭제 (BOARD_15)
        
        Args:
            article_id: 삭제할 게시글 ID
        
        Returns:
            dict: 삭제 결과
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/delete/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 게시글 좋아요
    # =========================================================

    def like_article(self, article_id, is_add=True):
        """
        게시글 좋아요 추가/제거 (BOARD_06, BOARD_08)
        
        Args:
            article_id: 게시글 ID
            is_add: True=추가, False=제거
        
        Returns:
            dict: 결과
        """
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/like/{action}/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 게시글 목록 조회
    # =========================================================

    def get_list(self, skip=0, count=10, **kwargs):
        """
        게시글 목록 조회 (BOARD_01~05)
        
        Args:
            skip: 건너뛸 개수 (페이지네이션)
            count: 조회할 개수
            filter_title: 제목 검색 (선택)
            sort_by: 정렬 기준 (선택) - created_asc, created_desc
        
        Returns:
            list: 게시글 목록
        """
        read_url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article"
        params = {"skip": skip, "count": count}
        
        # raise_error 키 제거
        if 'raise_error' in kwargs:
            del kwargs['raise_error']
        
        # headers 추출
        extra_headers = kwargs.pop('headers', None)
        
        # 나머지 파라미터 추가
        params.update(kwargs)
        
        return self._send_request("GET", read_url, params=params, extra_headers=extra_headers)

    # =========================================================
    # 댓글 CRUD
    # =========================================================

    def create_comment(self, article_id, content, is_secret=False):
        """
        댓글 작성 (BOARD_16)
        
        Args:
            article_id: 게시글 ID
            content: 댓글 내용
            is_secret: 비밀 댓글 여부
        
        Returns:
            dict: 생성 결과 (article_comment_id 포함)
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_comment(self, comment_id, article_id, content):
        """
        댓글 수정 (BOARD_19)
        
        Args:
            comment_id: 댓글 ID
            article_id: 게시글 ID
            content: 수정할 내용
        
        Returns:
            dict: 수정 결과
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "article_comment_id": comment_id,
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    def delete_comment(self, comment_id, article_id):
        """
        댓글 삭제 (BOARD_20)
        
        Args:
            comment_id: 댓글 ID
            article_id: 게시글 ID
        
        Returns:
            dict: 삭제 결과
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/delete/"
        payload = {
            "article_comment_id": comment_id,
            "board_article_id": article_id,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 댓글 좋아요
    # =========================================================
    
    def like_comment(self, comment_id, is_add=True):
        """
        댓글 좋아요 추가/제거 (BOARD_07, BOARD_09)
        
        Args:
            comment_id: 댓글 ID
            is_add: True=추가, False=제거
        
        Returns:
            dict: 결과
        """
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/like/{action}/"
        payload = {"article_comment_id": comment_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 댓글 목록 조회
    # =========================================================

    def get_comments(self, article_id, offset=0, count=20, sort_by=None):
        """
        댓글 목록 조회 (BOARD_17, BOARD_18)
        
        Args:
            article_id: 게시글 ID
            offset: 건너뛸 개수
            count: 조회할 개수
            sort_by: 정렬 JSON 문자열 (선택)
                     예: '{"key":"created_datetime","order":"desc"}'
        
        Returns:
            dict: 전체 응답 (article_comments 키 포함)
        """
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/list/"
        params = {
            "board_article_id": article_id,
            "classroom_id": CLASSROOM_ID,
            "offset": offset,
            "count": count
        }
        
        if sort_by:
            params["sort_by"] = sort_by
        
        return self._send_request("GET", url, params=params)