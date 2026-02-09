"""
2026-02-06 심다영
게시판(Board) API 유틸리티 클래스
- 게시글/댓글 CRUD, 좋아요, 목록 조회 기능
- Multipart/form-data 전송 방식 사용
"""
from utils.config import CLASSROOM_ID, ORG_NAME, REST_BASE_URL, CLASSROOM_BASE_URL


class BoardAPI:
    """게시판 API 래퍼 클래스"""
    
    WRITE_PATH = "/org/qatrack/board/article"

    def __init__(self, client, org_name=ORG_NAME):
        self.client = client
        self.client.session.headers.update({
            "x-elice-org-name-short": org_name
        })

    def _send_request(self, method, url, payload=None, params=None, extra_headers=None, files=None):
        headers = dict(self.client.session.headers)
        headers["Content-Type"] = None

        if extra_headers:
            headers.update(extra_headers)

        if method == "POST":
            multi_part_data = {}
            if payload:
                for key, value in payload.items():
                    if value is not None:
                        multi_part_data[key] = (None, str(value))
            if files:
                multi_part_data.update(files)
            response = self.client.session.post(url, files=multi_part_data, headers=headers)
        else:
            response = self.client.session.get(url, params=params, headers=headers)
            
        self.client.status_code = response.status_code

        try:
            return response.json()
        except:
            return {"detail": response.text}

    # =========================================================
    # 게시글 CRUD
    # =========================================================

    def create_article(self, title, content, is_secret=True, files=None):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "title": title,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    def update_article(self, article_id, title, content, is_secret=True, files=None):
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
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/delete/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    def like_article(self, article_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/like/{action}/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 게시글 목록 조회
    # =========================================================

    def get_list(self, skip=0, count=10, **kwargs):
        read_url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article"
        params = {}
        
        if skip is not None:params["skip"] = skip 
        if count is not None: params["count"] = count
        if 'raise_error' in kwargs: del kwargs['raise_error']
        extra_headers = kwargs.pop('headers', None)
        
        params.update(kwargs)
        return self._send_request("GET", read_url, params=params, extra_headers=extra_headers)

    def get_article(self, article_id):
        target_id = str(article_id)
        page_size = 40
        max_pages = 3
        for page in range(max_pages):
            skip_count = page * page_size
            response = self.get_list(skip=skip_count, count=page_size)
            articles = []
            if isinstance(response, list):
                articles = response
            elif isinstance(response, dict):
                if "detail" in response or "_result" in response:
                    continue
                articles = response.get("articles") or response.get("data") or response.get("results") or []
            if not articles:
                break
            for item in articles:
                if str(item.get("id")) == target_id:
                    return item
        return None

    # =========================================================
    # 댓글 CRUD
    # =========================================================

    def create_comment(self, article_id, content, is_secret=False):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_comment(self, comment_id, article_id, content):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "article_comment_id": comment_id,
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    def delete_comment(self, comment_id, article_id):
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/delete/"
        payload = {
            "article_comment_id": comment_id,
            "board_article_id": article_id,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)
    
    def like_comment(self, comment_id, is_add=True):
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/like/{action}/"
        payload = {"article_comment_id": comment_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 댓글 목록 조회 (수정됨: ordering 사용)
    # =========================================================

    def get_comments(self, article_id, offset=0, count=20, sort=None):
        """댓글 목록 조회"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/list/"
        
        params = {
            "board_article_id": article_id, 
            "offset": offset,
            "count": count,
            "classroom_id": CLASSROOM_ID
        }
        
        if sort:
            # 🚨 [Try 5] 'ordering' 파라미터로 변경 (Django 표준)
            params["ordering"] = sort
        print(f" - URL: {url}")
        print(f" - Params: {params}")

        return self._send_request("GET", url, params=params)