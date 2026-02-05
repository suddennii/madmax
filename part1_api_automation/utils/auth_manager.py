# 로그인 API 호출, 로그인 토큰 캐싱
from utils.config import config

class AuthManager:
    @staticmethod
    def get_token():
        return config["token"]
    @staticmethod
    def get_extoken():
        return config["extoken"]
