def student_course(account_id, classroom_id, offset, count):
        return (
        f"/student/{account_id}/course"
        f"?classroom_id={classroom_id}&offset={offset}&count={count}"
    )
