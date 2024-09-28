from datetime import timedelta, datetime
import random
import re
import string
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config

from database import get_db
from domain.user.router import get_current_user
from domain.history import crud as history_crud
from domain.history import schema as history_schema

from models import *

router = APIRouter(
    prefix="/history",
)


@router.post("")
async def create_history(
    history_create: history_schema.HistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 기록 추가
    
    ## Request Body
    - category: int (1: 공부, 2: 운동, 3: 기타)
    - duration: int (초 단위)
    - content: str (내용)
    """
    
    
    return history_crud.create_history(db, history_create, current_user)

@router.get("/me", response_model=history_schema.MyInfo)
async def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 내 기록 조회
    
    ## Response Body
    - durations: 
        - 1: 이번달 공부 시간 (초)
        - 2: 이번달 운동 시간 (초)
        - 3: 이번달 기타 시간 (초)
    """
    
    result = history_crud.get_my_history(db, current_user)
    categories = [1, 2, 3]
    history_dict = {row.category: row.total_duration for row in result}
    full_result = {
        cat: history_dict.get(cat, 0)
        for cat in categories
    }
    print(full_result)
    
    
    return history_schema.MyInfo(
        durations=full_result
    )


@router.get("/ranking/{category}", response_model=list[history_schema.Ranking])
async def get_ranking(
    category: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 랭킹 조회
    
    자신이 팔로우하는 사람들의 랭킹을 조회합니다.
    
    ## Request Query
    - category: int (1: 공부, 2: 운동, 3: 기타)
    
    ## Response Body
    - ranking: List
        - username: str
        - duration: int
    """
    
    result = history_crud.get_ranking(db, current_user.id, category)
    
    print(result)
    return result


@router.get("/weekly", response_model=history_schema.Weekly)
def get_my_history_weekly(
    year: int = Query(None, ge=2000, le=2100),
    month: int = Query(None, ge=1, le=12),
    week: int = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 주간 기록 조회
    
    ## Request Query
    - year: int (2000 ~ 2100)
    - month: int (1 ~ 12)
    - week: int (1 ~ 5)
    
    ## Response Body
    - monday: int
    - tuesday: int
    - wednesday: int
    - thursday: int
    - friday: int
    - saturday: int
    - sunday: int
    - everage: 평균
    - max: 최대
    - study_total: 공부 총합
    - exercise_total: 운동 총합
    - etc_total: 기타 총합
    """
    
    
    # 주간 시작일과 종료일 계산
    if year is None or month is None or week is None:
        raise HTTPException(status_code=400, detail="Year, month, and week must be provided.")

    first_day_of_month = datetime(year, month, 1)
    first_day_of_week = first_day_of_month + timedelta(weeks=week - 1)

    # 주간 시작일 (월요일)과 종료일 (일요일)
    monday = first_day_of_week - timedelta(days=first_day_of_week.weekday())
    sunday = monday + timedelta(days=6)

    # 요일별 duration 집계
    week_data = {
        "monday": 0,
        "tuesday": 0,
        "wednesday": 0,
        "thursday": 0,
        "friday": 0,
        "saturday": 0,
        "sunday": 0,
        "study_total": 0,
        "exercise_total": 0,
        "etc_total": 0,
        "average": 0,
        "max": 0,
    }

    results = db.query(
        History.category,
        func.sum(History.duration).label("total_duration")
    ).filter(
        History.user_id == current_user.id,
        History.created_at >= monday,
        History.created_at <= sunday
    ).group_by(History.category).all()

    # 카테고리별 duration 집계
    for category, total_duration in results:
        if category == 1:  # 공부
            week_data["study_total"] += total_duration
        elif category == 2:  # 운동
            week_data["exercise_total"] += total_duration
        elif category == 3:  # 기타
            week_data["etc_total"] += total_duration

        # 요일별 총합 집계
        for i in range(7):
            day = monday + timedelta(days=i)
            if day.date() == category:
                week_data[day.strftime("%A").lower()] += total_duration

    # 평균과 최대값 계산
    total_duration = (
        week_data["study_total"] +
        week_data["exercise_total"] +
        week_data["etc_total"]
    )
    
    week_data["average"] = int(total_duration / 7 if total_duration else 0)
    week_data["max"] = max(week_data["study_total"], week_data["exercise_total"], week_data["etc_total"])

    return week_data


@router.get("/monthly", response_model=history_schema.Monthly)
async def get_my_history_monthly(
    year: int = Query(None, ge=2000, le=2100),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 월간 기록 조회
    
    ## Request Query
    - year: int (2000 ~ 2100)
    - month: int (1 ~ 12)
    
    ## Response Body
    - days: List[int]
    - average: int
    - max: int
    - study_total: int
    - exercise_total: int
    - etc_total: int
    """
    

    # 일별 기록 조회
    days = [0] * 31  # 최대 31일로 초기화
    study_total = 0
    exercise_total = 0
    etc_total = 0

    # 해당 월의 기록 조회
    records = db.query(
        History.created_at,
        History.duration,
        History.category
    ).filter(
        History.user_id == current_user.id,
        func.extract("year", History.created_at) == year,
        func.extract("month", History.created_at) == month
    ).all()

    # 기록 처리
    for record in records:
        day = int(record.created_at.day) - 1  # 0-indexed
        days[day] += record.duration

        # 카테고리에 따라 총합 계산
        if record.category == 1:
            study_total += record.duration
        elif record.category == 2:
            exercise_total += record.duration
        elif record.category == 3:
            etc_total += record.duration

    # 평균과 최대 값 계산
    total_duration = sum(days)
    average = total_duration // (len([day for day in days if day > 0]) or 1)
    max_duration = max(days)

    return history_schema.Monthly(
        days=days,
        average=average,
        max=max_duration,
        study_total=study_total,
        exercise_total=exercise_total,
        etc_total=etc_total
    )
