import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "base_url": "https://api-account.elice.io",
    "token": os.getenv("TOKEN"),
}

#-----
# API 기본 설정
#-----
BASE_URL = "https://qatrack.elice.io"
CLASSROOM_URL = "https://api-classroom.elice.io"
CLASSROOM_ID = "a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc"

# -----
# 기타 설정
# -----
TIMEOUT = 10  # API 요청 타임아웃 (초)
RETRY = 3     # 실패 시 재시도 횟수
