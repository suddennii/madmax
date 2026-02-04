import requests
from utils.config import config
from utils.logger import logger

class ApiClient:
    # BASE URL 관리
    def __init__(self, token=None):
        # 토큰을 안 넘기면 기본값이 None
        self.base_url=config["base_url"]
        # config 라는 객체에 base_url 값을 가져와서 변수에 저장
        # 호출할 API 서버의 기본 주소
        self.session = requests.Session()
        # 세선 재사용하면서 쿠키, 헤더 등 공유
        self.session.headers.update({
            "Content-Type":"application/json",
        })
        # 이 세션으로 보내는 모든 요청에 기본 헤더 추가, json 형식으로 보낼거임
        if token:
            self.session.headers.update({"Authorization":f"Bearer {token}"})
        # 만약 토큰이 넘어오면 토큰 값 세션에 추가

    def get(self, path, params=None,raise_error=True):
        # get 메서드 공통화
        url=self.base_url + path # self.base_url과 전달받은 경로 path를 합쳐서 최종 url이 됨
        logger.info(f"[GET] {url} params={params}") # 로그남기기
        response = self.session.get(url, params=params) #requests.Session을 활용하여 GET요청 보내기, 파라미터들

        if raise_error: # Negative 시나리오 처리
            return self._handle_response(response) 
        return self._handle_response(response) # Positive 시나리오 처리

    def post(self, path, data=None,raise_error=True):
        # post 메서드 공통화
        url = self.base_url + path
        logger.info(f"[POST] {url} body={data}")
        response = self.session.post(url, json=data)
        if raise_error: # Negative 시나리오 처리
            return self._handle_response(response)
        return self._handle_response(response) # Positive 시나리오 처리
    
    def _handle_response(self, response):
        return response

