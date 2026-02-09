"""
파일 목적 : 프로젝트 전역에서 사용하는 환경 변수 및 설정값을 관리하는 Config 모듈

작성자 : 박지우 / 수정일 : 2026-02-09

설정 목적 :
- API 호출에 필요한 Base URL, Token 등 환경 기반 설정을 중앙에서 관리한다.
- 테스트 및 실행 환경에 따라 달라지는 값을 .env 기반으로 로드하여 일관성 있게 사용한다.
- 페이징, 기본 파라미터 등 공통 설정값을 한 곳에서 정의하여 재사용성을 높인다.

기타 주의 사항 :
- 민감 정보는 반드시 .env 파일을 통해 관리한다.
- config.py는 로직을 포함하지 않고, 설정/상수만을 관리하는 것을 원칙으로 한다.
"""

import os
from dotenv import load_dotenv
import yaml
from pathlib import Path

load_dotenv()

# ============================================================
# 1) API 기본 설정 (환경 변수 기반)
#    - 서비스별 Base URL
#    - 인증 토큰 / 만료 토큰
# ============================================================
config = {
    "account_base_url": os.getenv("ACCOUNT_BASE_URL"),
    "dash_base_url": os.getenv("DASH_BASE_URL"),
    "classroom_base_url": os.getenv("CLASSROOM_BASE_URL"),
    "rest_base_url": os.getenv("REST_BASE_URL"),
    "course_base_url": os.getenv("COURSE_BASE_URL"),
    "token": os.getenv("TOKEN"),
    "extoken": os.getenv("EXTOKEN"),
}

# ============================================================
# 2) YAML 로더
#    - 설정 파일(.yaml) 읽기용 유틸 함수
# ============================================================
def load_yaml(path:str):
    file_path=Path(path)
    with file_path.open(encoding='utf-8') as f:
        return yaml.safe_load(f)

# ============================================================
# 3) 공통 환경 설정값
#    - 계정/클래스룸 ID
#    - 타임아웃/재시도 횟수
# ============================================================
CLASSROOM_ID = os.getenv("CLASSROOM_ID")
ACCOUNT_ID = int(os.getenv("ACCOUNT_ID"))
ACCOUNT_ID2 = int(os.getenv("ACCOUNT_ID2"))
TIMEOUT = int(os.getenv("TIMEOUT", 10))
RETRY = int(os.getenv("RETRY", 3))
REST_BASE_URL = config["rest_base_url"]
CLASSROOM_BASE_URL = config["classroom_base_url"]

# ============================================================
# 4) 상수 정의
# ============================================================
PAGE_SKIP = int(os.getenv("PAGE_SKIP", 0))
PAGE_COUNT = int(os.getenv("PAGE_COUNT", 20))
TARGET_COURSE = os.getenv("TARGET_COURSE", "SANDBOX")
ORG_NAME = os.getenv("ORG_NAME", "qatrack")
ELICE_COURSE_ID = int(os.getenv("ELICE_COURSE_ID", 766557))
LECTURE_ID = int(os.getenv("LECTURE_ID", 6644275))

# ============================================================
# 5) API 호출 시 기본 파라미터
#    - 강의 ID, locator type, 페이징, 코스 ID 등
# ============================================================
DEFAULT_PARAMS = {
    "filter_lecture_id": LECTURE_ID,
    "filter_locator_type": int(os.getenv("DEFAULT_FILTER_LOCATOR_TYPE", 0)),
    "skip": int(os.getenv("DEFAULT_SKIP", 0)),
    "count": int(os.getenv("DEFAULT_COUNT", 40)),
    "elice_course_id": ELICE_COURSE_ID
}
