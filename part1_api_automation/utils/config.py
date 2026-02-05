import os
from dotenv import load_dotenv
import json
from utils.endpoints import student_course

load_dotenv()

config = {
    "account_base_url": "https://api-account.elice.io",
    "dash_base_url" : "https://api-dashboard.elice.io",
    "classroom_base_url" :"https://api-classroom.elice.io",
    "rest_base_url":"https://api-rest.elice.io",
    "course_base_url":"https://api-course.elice.io",
    "token": os.getenv("TOKEN"),
    "extoken" : os.getenv("EXTOKEN")
}


def basic_json():
    path = os.path.join("test_data","basic.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_student_course_endpoint(params):
    return student_course(
        account_id=params.get("account_id"),
        classroom_id=params.get("classroom_id"),
        offset=params.get("offset"),
        count=params.get("count")
    )

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
ORG_NAME = "qatrack"
ELICE_COURSE_ID = 766557
LECTURE_ID = 6644275
DEFAULT_PARAMS = {
    "filter_lecture_id": LECTURE_ID,
    "filter_locator_type": 0,
    "skip": 0,
    "count": 40,
    "elice_course_id": ELICE_COURSE_ID
}