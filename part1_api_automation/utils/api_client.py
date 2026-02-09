import requests
from utils.config import config
from utils.logger import logger

class ApiClient:
    def __init__(self, token=None, url_type="account"):
        key = f"{url_type}_base_url"
        self.base_url = config[key]

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _request(self, method, path, *, params=None, data=None):
        url = self.base_url + path
        logger.info(f"[{method.upper()}] {url} params={params} body={data}")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data
        )
        return self._handle_response(response)

    def get(self, path, params=None):
        return self._request("get", path, params=params)

    def post(self, path, data=None):
        return self._request("post", path, data=data)

    def patch(self, path, data=None):
        return self._request("patch", path, data=data)

    def _handle_response(self, response):
        self.status_code = response.status_code
        if response.status_code >= 400:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        try:
            return response.json()
        except ValueError:
            return response.text
