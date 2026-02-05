"""
2026-02-25 심다영
게시판(Board) API 유틸리티 클래스
- 게시글 생성, 조회, 수정, 삭제, 좋아요 기능 포함
"""
# D:\Elice_QA\final_project\madmax\part1_api_automation\utils\board_api.py

import json

class BoardAPI:
    REST_URL = "https://api-rest.elice.io"
    WRITE_PATH = "/org/qatrack/board/article"

    READ_URL = "https://api-classroom.elice.io/classroom/a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc/article"
    CLASSROOM_ID = "a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc"

    def __init__(self, client):
        self.client = client
        # 공통 헤더 설정
        self.client.session.headers.update({
            "x-elice-org-name-short": "qatrack"
        })

    def _send_request(self, method, url, payload=None, params=None, extra_headers=None):
        """
        [핵심] 좀비 헤더(application/json)를 죽이고 Multipart로 전송
        """
        headers = dict(self.client.session.headers)
        headers["Content-Type"] = None
            
        if extra_headers:
            headers.update(extra_headers)

        multi_part_data = None
        if payload:
            multi_part_data = {}
            for key, value in payload.items():
                # (파일명, 데이터) -> 파일명을 None으로 주면 일반 텍스트 필드로 인식됨
                multi_part_data[key] = (None, str(value))

        if method == "POST":
            response = self.client.session.post(url, files=multi_part_data, headers=headers)
        else:
            response = self.client.session.get(url, params=params, headers=headers)
            
        self.client.status_code = response.status_code
        try:
            return response.json()
        except:
            return response.text

    # --- 기능 함수들 (그대로 유지) ---

    def create_article(self, title, content, is_secret=True):
        url = f"{self.REST_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "title": title, "content": content,
            "classroom_id": self.CLASSROOM_ID, "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_article(self, article_id, title, content, is_secret=True):
        url = f"{self.REST_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "board_article_id": article_id, "title": title, "content": content,
            "classroom_id": self.CLASSROOM_ID, "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def delete_article(self, article_id):
        url = f"{self.REST_URL}{self.WRITE_PATH}/delete/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    def like_article(self, article_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{self.REST_URL}{self.WRITE_PATH}/like/{action}/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    def get_list(self, skip=0, count=10, **kwargs):
        params = {"skip": skip, "count": count}
        if 'raise_error' in kwargs: del kwargs['raise_error']
        params.update(kwargs)
        extra_headers = kwargs.pop('headers', None)
        return self._send_request("GET", self.READ_URL, params=params, extra_headers=extra_headers)

    def create_comment(self, article_id, content, is_secret=False):
        url = f"{self.REST_URL}/org/qatrack/board/article/comment/edit/"
        payload = {
            "board_article_id": article_id, "content": content,
            "classroom_id": self.CLASSROOM_ID, "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_comment(self, comment_id, article_id, content):
        url = f"{self.REST_URL}/org/qatrack/board/article/comment/edit/"
        payload = {
            "article_comment_id": comment_id, "board_article_id": article_id,
            "content": content, "classroom_id": self.CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    def delete_comment(self, comment_id, article_id):
        url = f"{self.REST_URL}/org/qatrack/board/article/comment/delete/"
        payload = {
            "article_comment_id": comment_id, "board_article_id": article_id,
            "classroom_id": self.CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)
    
    def like_comment(self, comment_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{self.REST_URL}/org/qatrack/board/article/comment/like/{action}/"
        payload = {"article_comment_id": comment_id}
        return self._send_request("POST", url, payload=payload)