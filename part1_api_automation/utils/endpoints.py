def student_course(
    account_id=None, classroom_id=None, filter_title=None,
    offset=None, skip=None, count=None
):
    # 1) base path 결정
    if account_id:
        base = f"/student/{account_id}/course?"
    elif classroom_id:
        base = f"/classroom/{classroom_id}/course?"
    else:
        base = "/student/course?"  # fallback
    # 2) query params 구성
    params = []
    if classroom_id is not None:
        params.append(f"classroom_id={classroom_id}")

    if filter_title is not None:
        params.append(f"filter_title={filter_title}")
    if offset is not None:
        params.append(f"offset={offset}")  # skip = offset 매핑
    if skip is not None:
        params.append(f"skip={skip}")  # skip = offset 매핑  
    if count is not None:
        params.append(f"count={count}")

    # 3) 최종 URL 반환
    return base + "&".join(params)


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
