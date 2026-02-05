def student_course(account_id=None, classroom_id=None, offset=None, count=None):
    # 기본 path
    if account_id is None:
        base = "/student/course?" #account가 없으면 /stujdent//course 이런식으로 되서 없는 경우 해당 base로 고정
    else: 
        base = f"/student/{account_id}/course?"
    params = []
    if classroom_id is not None:
        params.append(f"classroom_id={classroom_id}")
    if offset is not None:
        params.append(f"offset={offset}")
    if count is not None:
        params.append(f"count={count}")

    return base + "&".join(params)
