import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "account_base_url": "https://api-account.elice.io",
    "dash_base_url" : "https://api-dashboard.elice.io",
    "classroom_base_url" :"https://api-classroom.elice.io",
    "rest_base_url":"https://api-rest.elice.io",
    "token": os.getenv("TOKEN"),
}

#-----
# API 기본 설정
#-----
QATRACK_URL = "https://qatrack.elice.io"
CLASSROOM_URL = "https://api-classroom.elice.io"
CLASSROOM_ID = "a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc"

# -----
# 기타 설정
# -----
TIMEOUT = 10  # API 요청 타임아웃 (초)
RETRY = 3     # 실패 시 재시도 횟수

# === 상수 정의 ===
PAGE_SKIP = 0
PAGE_COUNT = 20
TARGET_COURSE = "SANDBOX"