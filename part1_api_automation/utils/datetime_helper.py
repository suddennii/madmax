'''
작성자 : 신윤아 / 작성일 : 26.02.09
함수 목적 
 - params에 들어갈 dt_start_ge,dt_start_le 값 자동 생성(당일기준)
'''
from datetime import datetime, timezone, timedelta

def select_time(
    base_dt=None,
    offset_days=0,
    offset_hours=0,
    offset_minutes=0,
):
    if base_dt is None:
        dt = datetime.now(timezone.utc)
    else:
        dt = base_dt.astimezone(timezone.utc)

    dt += timedelta(
        days=offset_days,
        hours=offset_hours,
        minutes=offset_minutes
    )

    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")