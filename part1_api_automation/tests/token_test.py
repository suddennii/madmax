from utils.auth_manager import AuthManager
from utils.api_client import ApiClient

# 인증이 필요한 API 엔드포인트 (네 서비스에 맞게 수정)
TEST_ENDPOINT = "/account/me"   # 예: /users/me, /profile 등

def main():
    token = AuthManager.get_token()
    client = ApiClient(token=token)

    print("=== 토큰 테스트 시작 ===")
    print(f"요청 엔드포인트: {TEST_ENDPOINT}")

    response = client.get(TEST_ENDPOINT, raise_error=False)

    print("\n=== 결과 ===")
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

if __name__ == "__main__":
    main()
