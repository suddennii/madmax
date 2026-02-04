import requests
from utils.config import config
from utils.logger import logger

class ApiClient:
    def __init__(self, token=None):
        self.base_url=config["base_url"]
        