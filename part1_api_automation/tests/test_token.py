"""
파일 목적 : 인증 토큰이 정상적으로 동작하는지 확인하기 위한 간단한 테스트 스크립트

작성자 : 박지우 / 작성일 : 2026-02-04

테스트 목적 :
- AuthManager에서 불러온 토큰이 실제 API 요청에 정상적으로 사용되는지 검증한다.
- 토큰 유효성, API 연결 상태, 기본 응답 구조 등을 빠르게 점검하는 용도.

기타 주의 사항 :
- TEST_ENDPOINT는 서비스 환경에 맞게 수정해야 한다.
- 실제 운영 토큰을 사용할 경우 민감 정보가 노출되지 않도록 주의한다.
"""

from utils.auth_manager import AuthManager
from utils.api_client import ApiClient

# 인증이 필요한 API 엔드포인트 (네 서비스에 맞게 수정)
TEST_ENDPOINT = "/account/me"   # 예: /users/me, /profile 등

def test_main():
    token = AuthManager.get_token()
    client = ApiClient(token=token)

    print("=== 토큰 테스트 시작 ===")
    print(f"요청 엔드포인트: {TEST_ENDPOINT}")

    response = client.get(TEST_ENDPOINT, raise_error=False)

    print("\n=== 결과 ===")
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)