"""
파일 목적 : 로그인 API에서 발급된 인증 토큰을 관리하고 제공하는 Auth 모듈

작성자 : 박지우 / 작성일 : 2026-02-04
작성자 : - / 수정일 : -

설정 목적 :
- .env 기반으로 로드된 로그인 토큰(token, extoken)을 중앙에서 관리한다.
- API 호출 시 필요한 인증 정보를 일관된 방식으로 제공한다.
- 토큰을 직접 하드코딩하거나 여러 파일에서 중복 관리하는 문제를 방지한다.

기타 주의 사항 :
- 토큰은 config.py에서 로드되므로, AuthManager는 단순한 getter 역할만 수행한다.
- 토큰 갱신 로직이 필요해지면 이 모듈에서 확장할 수 있다.
"""

from utils.config import config

class AuthManager:
    @staticmethod
    def get_token():
        return config["token"]
    @staticmethod
    def get_extoken():
        return config["extoken"]
