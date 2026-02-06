# def student_course(account_id=None, classroom_id=None, offset=None, count=None):
#     # 기본 path
#     if account_id is None:
#         base = "/student/course?" #account가 없으면 /stujdent//course 이런식으로 되서 없는 경우 해당 base로 고정
#     else: 
#         base = f"/student/{account_id}/course?"
#     params = []
#     if classroom_id is not None:
#         params.append(f"classroom_id={classroom_id}")
#     if offset is not None:
#         params.append(f"offset={offset}")
#     if count is not None:
#         params.append(f"count={count}")

#     return base + "&".join(params)

# def build_classroom_course_endpoint(params):
#     classroom_id = params.get("classroom_id")
#     filter_title = params.get("filter_title")
#     skip = params.get("skip")
#     count = params.get("count")

#     base = f"/classroom/{classroom_id}/course?"

#     query = []

#     if filter_title is not None:
#         query.append(f"filter_title={filter_title}")

#     if skip is not None:
#         query.append(f"skip={skip}")

#     if count is not None:
#         query.append(f"count={count}")

#     return base + "&".join(query)

def student_course(
    account_id=None,
    classroom_id=None,
    filter_title=None,
    offset=None,
    skip=None,
    count=None
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