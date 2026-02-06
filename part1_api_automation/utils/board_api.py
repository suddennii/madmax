"""
2026-02-05 심다영
게시판(Board) API 유틸리티 클래스
- 게시글 생성, 조회, 수정, 삭제, 좋아요 기능 포함

2026-02-06 심다영
게시판(Board) API 유틸리티 클래스
- 파일 첨부 기능 지원 (업그레이드됨)
"""
from utils.config import config, CLASSROOM_ID, ORG_NAME, REST_BASE_URL, CLASSROOM_BASE_URL

class BoardAPI:
    WRITE_PATH = "/org/qatrack/board/article"
    
    def __init__(self, client):
        self.client = client
        self.client.session.headers.update({
            "x-elice-org-name-short": ORG_NAME
        })

    def _send_request(self, method, url, payload=None, params=None, extra_headers=None, files=None):
        """
        [수정됨] 텍스트 필드(payload)와 파일(files)을 함께 전송하도록 개선
        """
        headers = dict(self.client.session.headers)
        headers["Content-Type"] = None # Multipart 자동 설정을 위해 제거
            
        if extra_headers:
            headers.update(extra_headers)

        # Multipart 데이터 조립
        multi_part_data = {}
        
        # 1. 일반 텍스트 데이터 처리
        if payload:
            for key, value in payload.items():
                multi_part_data[key] = (None, str(value))
        
        # 2. [NEW] 진짜 파일 데이터 병합
        if files:
            multi_part_data.update(files)

        if method == "POST":
            # files 파라미터에 텍스트+파일을 모두 넣어서 보냄
            response = self.client.session.post(url, files=multi_part_data, headers=headers)
        else:
            response = self.client.session.get(url, params=params, headers=headers)
            
        self.client.status_code = response.status_code
        try:
            return response.json()
        except:
            return response.text

    # --- 기능 함수들 (files 인자 추가됨) ---

    def create_article(self, title, content, is_secret=True, files=None):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "title": title, "content": content,
            "classroom_id": CLASSROOM_ID, 
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    def update_article(self, article_id, title, content, is_secret=True, files=None):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "board_article_id": article_id, "title": title, "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    # ... 나머지 함수들 (delete_article, like_article, get_list 등)은 기존과 동일 ...
    # (너무 길어지니 아래는 생략했지만, 기존 코드를 그대로 두시면 됩니다)
    def delete_article(self, article_id):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/delete/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    def like_article(self, article_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/like/{action}/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    def get_list(self, skip=0, count=10, **kwargs):
        read_url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article"
        params = {"skip": skip, "count": count}
        if 'raise_error' in kwargs: del kwargs['raise_error']
        params.update(kwargs)
        extra_headers = kwargs.pop('headers', None)
        return self._send_request("GET", read_url, params=params, extra_headers=extra_headers)

    def create_comment(self, article_id, content, is_secret=False):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "board_article_id": article_id, "content": content,
            "classroom_id": CLASSROOM_ID, 
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_comment(self, comment_id, article_id, content):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "article_comment_id": comment_id, "board_article_id": article_id,
            "content": content, "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    def delete_comment(self, comment_id, article_id):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/delete/"
        payload = {
            "article_comment_id": comment_id, "board_article_id": article_id,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)
    
    def like_comment(self, comment_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/like/{action}/"
        payload = {"article_comment_id": comment_id}
        return self._send_request("POST", url, payload=payload)
    
    def get_comments(self, article_id):
        url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article/{article_id}/comment"
        return self._send_request("GET", url)