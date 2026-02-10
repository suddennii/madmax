"""
파일 목적 : 학생/강좌 관련 API 엔드포인트 URL을 생성하는 유틸리티 모듈

작성자 : 박지우 / 작성일 : 2026-02-04
작성자 : 박지우 / 수정일 : 2026-02-09

설정 목적 :
- student, classroom 기반의 강좌 조회/계정 조회 API 엔드포인트를 일관된 방식으로 생성한다.
- 테스트 및 서비스 코드에서 반복되는 URL 조립 로직을 모듈화하여 재사용성을 높인다.
- 파라미터 기반으로 동적으로 URL을 구성하여 코드 중복을 줄인다.

기타 주의 사항 :
- 엔드포인트 생성만 담당하며, 실제 API 호출 로직은 포함하지 않는다.
- 파라미터가 None일 경우 URL에 포함되지 않도록 주의한다.
"""


# ============================================================
# 학생-강좌 조회 엔드포인트 생성
# ------------------------------------------------------------
# account_id 또는 classroom_id를 기준으로 base path를 결정하고,
# 전달된 파라미터를 query string 형태로 조합하여 최종 URL을 반환한다.
# ============================================================
def student_course(
    account_id=None, classroom_id=None, filter_title=None,
    offset=None, skip=None, count=None
):
    if account_id:
        base = f"/student/{account_id}/course?"
    elif classroom_id:
        base = f"/classroom/{classroom_id}/course?"
    else:
        base = "/student/course?"  

    params = []
    if classroom_id is not None:
        params.append(f"classroom_id={classroom_id}")

    if filter_title is not None:
        params.append(f"filter_title={filter_title}")
    if offset is not None:
        params.append(f"offset={offset}")  
    if skip is not None:
        params.append(f"skip={skip}")  
    if count is not None:
        params.append(f"count={count}")

    # 3) 최종 URL 반환
    return base + "&".join(params)

# ============================================================
# 학생 계정 조회 엔드포인트 생성
# ------------------------------------------------------------
# account_id 기반으로 기본 path를 구성하고,
# classroom_id가 있을 경우 query string으로 추가한다.
# ============================================================
def student_account(  account_id=None, classroom_id=None):
    # 기본 path
    base = f"/student/{account_id}"
    # query params
    query = []
    if classroom_id is not None:
        query.append(f"classroom_id={classroom_id}")
    # 최종 URL
    if query:
        return base + "?" + "&".join(query)
    return base

# ============================================================
# 엔드포인트 빌더 (dict 기반 파라미터 입력)
# ------------------------------------------------------------
# 외부에서 params(dict)를 받아 student_course / student_account
# 엔드포인트를 생성하는 wrapper 함수.
# ============================================================
def build_student_course_endpoint(params):
    return student_course(
        account_id=params.get("account_id"),
        classroom_id=params.get("classroom_id"),
        filter_title=params.get("filter_title"),
        offset=params.get("offset"),
        skip=params.get("skip"),
        count=params.get("count")
    )
def build_student_account_endpoint(params):
    return student_account(
        account_id=params.get("account_id"),
        classroom_id=params.get("classroom_id")
    )
