"""
API Client

**작성자** : 박지우 / **작성일** : 26.02.04
**작성자** : 박지우 / **수정일** : 26.02.09

파일 목적:
- 대시보드/클래스룸 등 다양한 API 엔드포인트 호출을 위한 공통 HTTP 클라이언트 제공
- 인증 토큰, 기본 URL, 공통 헤더 설정을 일원화하여 테스트 코드의 중복 제거
"""

import requests
from utils.config import config
from utils.logger import logger

class ApiClient:
    """
    API 요청을 담당하는 공통 클라이언트 클래스.
    - url_type(dash/classroom/account 등)에 따라 base_url 자동 설정
    - Authorization 헤더 자동 적용
    - GET/POST/PATCH 요청 공통 처리
    """
    def __init__(self, token=None, url_type="account"):
        key = f"{url_type}_base_url"
        self.base_url = config[key]
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _request(self, method, path, *, params=None, data=None):
        #HTTP 요청 공통 처리 (로그 출력 + 응답 핸들링)
        url = self.base_url + path
        logger.info(f"[{method.upper()}] {url} params={params} body={data}")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data
        )
        return self._handle_response(response)

    # ---------------------------------------------------------
    # HTTP 메서드 래퍼
    # ---------------------------------------------------------
    def get(self, path, params=None):
        return self._request("get", path, params=params)

    def post(self, path, data=None):
        return self._request("post", path, data=data)

    def patch(self, path, data=None):
        return self._request("patch", path, data=data)
    
    # ---------------------------------------------------------
    # 응답 처리
    """
    - 400 이상이면 Exception 발생
    - JSON 응답이면 dict 반환
    - JSON 파싱 실패 시 text 반환
    """
    # ---------------------------------------------------------
    def _handle_response(self, response):
        self.status_code = response.status_code
        if response.status_code >= 400:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        try:
            return response.json()
        except ValueError:
            return response.text
