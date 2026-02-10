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
        """
        공통 요청 메서드
        - POST: Multipart/form-data 형식으로 전송
        - GET: Query parameter 형식으로 전송
        """
        headers = dict(self.client.session.headers)
        headers["Content-Type"] = None  # requests가 자동으로 multipart 설정

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
        """게시글 생성 (BOARD_11)"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/edit/"
        payload = {
            "title": title,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload, files=files)

    def update_article(self, article_id, title, content, is_secret=True, files=None):
        """게시글 수정 (BOARD_13, BOARD_14)"""
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
        """게시글 삭제 (BOARD_15)"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/delete/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 게시글 좋아요
    # =========================================================

    def like_article(self, article_id, is_add=True):
        """게시글 좋아요 추가/제거 (BOARD_06, BOARD_08)"""
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/like/{action}/"
        payload = {"board_article_id": article_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 게시글 목록 조회 및 단건 조회
    # =========================================================

    def get_list(self, skip=0, count=10, **kwargs):
        """게시글 목록 조회 (BOARD_01~05)"""
        read_url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article"
        
        params = {"skip": skip, "count": count}
        if 'raise_error' in kwargs:
            del kwargs['raise_error']
        
        extra_headers = kwargs.pop('headers', None)
        params.update(kwargs)
        
        return self._send_request("GET", read_url, params=params, extra_headers=extra_headers)

    def get_article(self, article_id):
        """특정 게시글 ID로 상세 정보 조회 (BOARD_12)"""
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
        """댓글 작성 (BOARD_16)"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID,
            "is_secret": str(is_secret).lower()
        }
        return self._send_request("POST", url, payload=payload)

    def update_comment(self, comment_id, article_id, content):
        """댓글 수정 (BOARD_19)"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/edit/"
        payload = {
            "article_comment_id": comment_id,
            "board_article_id": article_id,
            "content": content,
            "classroom_id": CLASSROOM_ID
        }
        return self._send_request("POST", url, payload=payload)

    def delete_comment(self, comment_id, article_id):
        """댓글 삭제 (BOARD_20)"""
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
        """댓글 좋아요 추가/제거 (BOARD_07, BOARD_09)"""
        action = "add" if is_add else "delete"
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/like/{action}/"
        payload = {"article_comment_id": comment_id}
        return self._send_request("POST", url, payload=payload)

    # =========================================================
    # 댓글 목록 조회
    # =========================================================

    def get_comments(self, article_id, offset=0, count=20, sort=None):
        """댓글 목록 조회 (Classroom API 사용으로 변경)"""
        # [변경 1] URL 변경: REST_BASE_URL -> CLASSROOM_BASE_URL
        # 패턴: /classroom/{cid}/article/{aid}/comment
        url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article/{article_id}/comment"
        
        # [변경 2] 파라미터 변경: offset -> skip (get_list와 통일), board_article_id 제거(URL에 포함됨)
        params = {
            "skip": offset, 
            "count": count
        }
        
        if sort:
            params["sort"] = sort
            
        # [디버깅] 변경된 요청 로그 확인
        print(f"\n[DEBUG] GET Comments (Classroom API) -> URL: {url}, Params: {params}")

        return self._send_request("GET", url, params=params)

        