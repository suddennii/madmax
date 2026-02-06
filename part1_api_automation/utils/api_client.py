import requests
from utils.config import config
from utils.logger import logger

class ApiClient:
    # BASE URL 관리
    def __init__(self, token=None, url_type="account"): #기본값 account
        key = f"{url_type}_base_url"
        self.base_url=config[key]
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type":"application/json",
        })
        if token:
            self.session.headers.update({"Authorization":f"Bearer {token}"})

    def get(self, path, params=None,raise_error=True):

        url=self.base_url + path 
        logger.info(f"[GET] {url} params={params}") 
        response = self.session.get(url, params=params) 
        if raise_error: 
            return self._handle_response(response) 
        return self._handle_response(response) 

    def post(self, path, data=None,raise_error=True):
        url = self.base_url + path
        logger.info(f"[POST] {url} body={data}")
        response = self.session.post(url, json=data)
        if raise_error:
            return self._handle_response(response)
        return self._handle_response(response)
    
    def patch(self, path, data=None,raise_error=True):
        url = self.base_url + path
        logger.info(f"[PATCH] {url}  body={data}")
        response = self.session.patch(url, json=data)
        if raise_error:
            return self._handle_response(response)
        return self._handle_response(response)
    
    def _handle_response(self, response):
        self.status_code = response.status_code
        if response.status_code >= 400:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        try:
            return response.json()
        except ValueError:
            return response.text

