"""
게시판(Board) API 유틸리티 클래스

작성자: 심다영 / 작성일: 2026-02-06
수정자: 심다영 / 수정일: 2026-02-10

수정 내역:
- conftest.py의 client(requests.Session) 호환 유지
- Multipart/form-data 전송 방식 적용
- 댓글 정렬(sort_by JSON) 파라미터 지원 추가 (Fix)
- board_api.status_code 사용 (client.status_code 대신)
- Assert 검증 강화 (TC ID별 명확한 에러 메시지)
- Negative TC 추가 (BOARD_12, BOARD_21~28)

[지원 기능]
- 게시글 CRUD (BOARD_11~15)
- 게시글 좋아요 (BOARD_06, BOARD_08)
- 목록 조회/검색/페이지네이션 (BOARD_01~05)
- 댓글 CRUD (BOARD_16~20)
- 댓글 좋아요 (BOARD_07, BOARD_09)
- 댓글 정렬 (BOARD_17, BOARD_18)
"""
import json # [추가] 정렬 파라미터 구성을 위해 필요
from utils.config import CLASSROOM_ID, ORG_NAME, REST_BASE_URL, CLASSROOM_BASE_URL


class BoardAPI:
    """
    게시판 API 래퍼 클래스
    
    conftest.py에서 주입받은 requests.Session 객체를 사용합니다.
    """
    
    WRITE_PATH = "/org/qatrack/board/article"

    def __init__(self, client, org_name=ORG_NAME):
        """
        BoardAPI 초기화
        
        Args:
            client: requests.Session 객체 (conftest.py에서 주입)
            org_name: 조직명 (기본값: qatrack)
        """
        # [주석 추가] conftest.py에서 생성된 session(헤더+쿠키 포함)을 그대로 사용합니다.
        self.client = client
        self.client.headers.update({
            "x-elice-org-name-short": org_name
        })

    @property
    def status_code(self):
        """마지막 요청의 상태 코드"""
        # [주석 추가] 테스트 코드에서 board_api.status_code로 접근 가능하게 함
        return getattr(self.client, 'status_code', None)

    def _send_request(self, method, url, payload=None, params=None, extra_headers=None, files=None):
        """
        공통 요청 메서드
        
        - POST: Multipart/form-data 형식으로 전송
        - GET: Query parameter 형식으로 전송
        """
        headers = dict(self.client.headers)
        
        # Multipart 전송 시 Content-Type을 None으로 설정
        headers["Content-Type"] = None

        if extra_headers:
            headers.update(extra_headers)

        response = None
        
        if method == "POST":
            # Multipart 데이터 구성
            multi_part_data = {}
            
            if payload:
                for key, value in payload.items():
                    if value is not None:
                        multi_part_data[key] = (None, str(value))
            
            if files:
                multi_part_data.update(files)
            
            response = self.client.post(url, files=multi_part_data, headers=headers)
        else:
            # GET 요청: None 값 필터링
            filtered_params = {k: v for k, v in (params or {}).items() if v is not None}
            response = self.client.get(url, params=filtered_params, headers=headers)
        
        # status_code 저장
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
        url = f"{CLASSROOM_BASE_URL}/classroom/{CLASSROOM_ID}/article"
        
        params = {}
        
        if skip is not None:
            params["skip"] = skip
        if count is not None:
            params["count"] = count
        
        extra_headers = kwargs.pop('headers', None)
        kwargs.pop('raise_error', None)
        params.update(kwargs)
        
        return self._send_request("GET", url, params=params, extra_headers=extra_headers)

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
                articles = response.get("articles") or \
                           response.get("data") or \
                           response.get("results") or []
            
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
    # 댓글 목록 조회 (수정됨: sort_by JSON 파라미터 사용)
    # =========================================================

    def get_comments(self, article_id, offset=0, count=20, sort=None):
        """댓글 목록 조회 (BOARD_17, BOARD_18)"""
        url = f"{REST_BASE_URL}{self.WRITE_PATH}/comment/list/"
        params = {
            "board_article_id": article_id,
            "offset": offset,
            "count": count
        }
        
        if sort:
            # [수정] URL에서 확인한 정확한 파라미터 구조 (JSON)
            # sort="id" 이면 오래된순(asc), sort="-id" 이면 최신순(desc)
            # 테스트 코드에서 "id", "-id"를 보내므로 이를 API 스펙에 맞게 변환
            
            order = "desc" if str(sort).startswith("-") else "asc"
            
            # JSON 문자열로 변환 (예: {"key":"created_datetime","order":"asc"})
            sort_payload = {"key": "created_datetime", "order": order}
            params["sort_by"] = json.dumps(sort_payload)
        
        return self._send_request("GET", url, params=params)