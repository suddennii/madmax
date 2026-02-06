"""
2026-02-06 심다영
게시글 작성/수정(REST API)과 목록 조회(Classroom API)를 위한 엔드포인트 분리
"""


import os
from dotenv import load_dotenv
from utils.endpoints import student_course
import yaml
from pathlib import Path

load_dotenv()

# === API 기본 설정 ===
config = {
    "account_base_url": os.getenv("ACCOUNT_BASE_URL"),
    "dash_base_url": os.getenv("DASH_BASE_URL"),
    "classroom_base_url": os.getenv("CLASSROOM_BASE_URL"),
    "rest_base_url": os.getenv("REST_BASE_URL"),
    "course_base_url": os.getenv("COURSE_BASE_URL"),
    "token": os.getenv("TOKEN"),
    "extoken": os.getenv("EXTOKEN"),
}

def load_yaml(path:str):
    file_path=Path(path)
    with file_path.open(encoding='utf-8') as f:
        return yaml.safe_load(f)

# === 기타 설정 === 
CLASSROOM_ID = os.getenv("CLASSROOM_ID")
ACCOUNT_ID = int(os.getenv("ACCOUNT_ID"))
TIMEOUT = int(os.getenv("TIMEOUT", 10))
RETRY = int(os.getenv("RETRY", 3))
REST_BASE_URL = config["rest_base_url"]
CLASSROOM_BASE_URL = config["classroom_base_url"]

# === 상수 정의 ===
PAGE_SKIP = int(os.getenv("PAGE_SKIP", 0))
PAGE_COUNT = int(os.getenv("PAGE_COUNT", 20))
TARGET_COURSE = os.getenv("TARGET_COURSE", "SANDBOX")
ORG_NAME = os.getenv("ORG_NAME", "qatrack")
ELICE_COURSE_ID = int(os.getenv("ELICE_COURSE_ID", 766557))
LECTURE_ID = int(os.getenv("LECTURE_ID", 6644275))


DEFAULT_PARAMS = {
    "filter_lecture_id": LECTURE_ID,
    "filter_locator_type": int(os.getenv("DEFAULT_FILTER_LOCATOR_TYPE", 0)),
    "skip": int(os.getenv("DEFAULT_SKIP", 0)),
    "count": int(os.getenv("DEFAULT_COUNT", 40)),
    "elice_course_id": ELICE_COURSE_ID
}

# === 학생-강좌 엔드포인트 빌드 ===
def build_student_course_endpoint(params):
    return student_course(
        account_id=params.get("account_id"),
        classroom_id=params.get("classroom_id"),
        filter_title=params.get("filter_title"),
        offset=params.get("offset"),
        skip=params.get("skip"),
        count=params.get("count")
    )
