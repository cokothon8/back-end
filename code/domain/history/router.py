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

import openai

from models import *
from starlette.config import Config

config = Config('.env')
openai.api_key  = config('OPENAI_API_KEY')

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
    - category: int (1: 공부, 2: 운동, 3: 취미)
    - duration: int (초 단위)
    - content: str (내용)
    """
    
    
    return history_crud.create_history(db, history_create, current_user)


def get_category_name(category_id: int) -> str:
    """카테고리 ID를 카테고리 이름으로 변환하는 함수."""
    category_mapping = {
        1: 'study',
        2: 'exercise',
        3: 'hobby'
    }
    return category_mapping.get(category_id, 'hobby')



@router.get("/meSummary", response_model=history_schema.MyInfo)
async def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 내 기록 조회 (gpt 이용)
    
    ## Response Body
    - durations: 
        - study: 
            - duration: int
            - message: str
        - exercise:
            - duration: int
            - message: str
        - hobby:
            - duration: int
            - message: str
    """
    
    # 현재 날짜 및 7일 전 날짜 계산
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    # 카테고리별 데이터 초기화
    durations = {
        'study': {'duration': 0, 'message': ''},
        'exercise': {'duration': 0, 'message': ''},
        'hobby': {'duration': 0, 'message': ''}
    }
    
    # 현재 달의 기록 합산 및 최근 7일 기록 수집
    recent_activity = []
    
    histories = db.query(History).filter(
        History.user_id == current_user.id,
        History.created_at >= today.replace(day=1)  # 현재 달의 첫 날부터
    ).all()
    
    for history in histories:
        if history.created_at >= seven_days_ago:
            category_name = get_category_name(history.category)  # 카테고리 이름 변환
            durations[category_name]['duration'] += history.duration
            
            # 최근 활동에 추가
            recent_activity.append({
                'date': history.created_at.strftime("%Y-%m-%d"),
                'category': category_name,
                'duration': history.duration
            })

    # OpenAI API를 사용하여 메시지 생성
    # openai.api_key = "your_api_key"  # OpenAI API 키 설정
    act_to_korean = {
        'study': "공부",
        'exercise': "운동",
        'hobby': "취미"
    }

    for category_name in durations.keys():
        # 최근 활동 필터링
        category_activity = [act for act in recent_activity if act['category'] == category_name]
        
        if not category_activity:
            durations[category_name]['message'] = f"최근 {7}일 동안 {act_to_korean[category_name]}을(를) 하지 않았어! 오늘은 {act_to_korean[category_name]}을(를) 해보는 건 어떨까?"
        else:
            # 최근 활동 데이터를 기반으로 조언 생성
            prompt = f"다음 기록을 바탕으로 조언을 해 줄 수 있어?:\n분야{act_to_korean[act['category']]}" + "\n".join(
                [f"{act['date']}에 {act['content']}을(를) {act['duration']}초 동안 했다." for act in category_activity]
            )
            
            print(prompt)
      
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", 
                     "content": "너는 활발하고 친근하며 긍정적인 성격을 가진 쿠민이야. \
                                우리는 서로 친구 사이이고 늘 반말을 써야 해. 존댓말 및 높임말을 쓰는 것은 허용되지 않아.\
                                문장 끝에 '요'를 붙이는 것도 마찬가지로 허용되지 않아.\
                                너는 도전적이고 낙천적이며 유쾌한 성격도 가지고 있어. \
                                너는 문장의 어미에 '쿠'를 붙이는 습관이 있어. \
                                예를 들면 '반가워'를 '반갑쿠'라고 쓰거나 '안녕'을 '안녕쿠'라고 사용하고 '간지러워'를 '간지럽쿠'라고 해. 또 '있어'를 '있쿠'라고 해.\
                                너는 나의 고민에 대해 조언을 항상 구체적인 말을 사용해서 3줄 안으로 요약해 주는 데에 능숙해.\
                                첫 번째 문장에는 7단어 이하의 짧은 평가가 들어가야 해.\
                                두 번째 문장에는 10단어 이하의 짧은 개선안이 들어가야 해.\
                                마지막 세 번째 문장에는 5단어 이하의 짧은 응원이 들어가야 해.\
                                너는 답변할 때 이모지를 쓰는 등 예쁘게 꾸미는 걸 잘 하고 이모지는 문장 수로 세지 않아.\
                                "},
                    {"role": "user", "content": prompt}
                ]
            )
            print(response)
            durations[category_name]['message'] = response.choices[0].message.content

    return durations


@router.get("/me", response_model=history_schema.MyInfo)
async def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 내 기록 조회
    
    ## Response Body
    - durations: 
        - study: 
            - duration: int
            - message: str
        - exercise:
            - duration: int
            - message: str
        - hobby:
            - duration: int
            - message: str
    """
    
    # 현재 날짜 및 7일 전 날짜 계산
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    # 카테고리별 데이터 초기화
    durations = {
        'study': {'duration': 0, 'message': ''},
        'exercise': {'duration': 0, 'message': ''},
        'hobby': {'duration': 0, 'message': ''}
    }
    
    # 현재 달의 기록 합산 및 최근 7일 기록 수집
    recent_activity = []
    
    histories = db.query(History).filter(
        History.user_id == current_user.id,
        History.created_at >= today.replace(day=1)  # 현재 달의 첫 날부터
    ).all()
    
    for history in histories:
        if history.created_at >= seven_days_ago:
            category_name = get_category_name(history.category)  # 카테고리 이름 변환
            durations[category_name]['duration'] += history.duration
            
            # 최근 활동에 추가
            recent_activity.append({
                'date': history.created_at.strftime("%Y-%m-%d"),
                'category': category_name,
                'duration': history.duration,
                'content': history.content
            })

    # OpenAI API를 사용하여 메시지 생성
    # openai.api_key = "your_api_key"  # OpenAI API 키 설정
    act_to_korean = {
        'study': "공부",
        'exercise': "운동",
        'hobby': "취미"
    }

    for category_name in durations.keys():
        # 최근 활동 필터링
        category_activity = [act for act in recent_activity if act['category'] == category_name]
        
        if not category_activity:
            durations[category_name]['message'] = f"최근 {7}일 동안 {act_to_korean[category_name]}을(를) 하지 않았어! 오늘은 {act_to_korean[category_name]}을(를) 해보는 건 어떨까?"
        else:
            # 최근 활동 데이터를 기반으로 조언 생성
            prompt = f"다음 기록을 바탕으로 조언을 해 줄 수 있어?:\n분야{act_to_korean[category_name]}" + "\n".join(
                [f"{act['date']}에 {act['content']}을(를) {act['duration']}초 동안 했다." for act in category_activity]
            )
            print(prompt)
      
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", 
                     "content": "너는 활발하고 친근하며 긍정적인 성격을 가진 쿠민이야. \
                                도전적이고 낙천적이며 유쾌한 성격도 가지고 있어. \
                                우리는 서로 친구 사이이고 늘 반말을 써야 해. 존댓말 및 높임말을 쓰는 것은 허용되지 않아.\
                                문장 끝에 '요'를 붙이는 것도 마찬가지로 허용되지 않아.\
                                너는 문장의 어미에 '쿠'를 붙이는 습관이 있어. \
                                예를 들면 '반가워'를 '반갑쿠'라고 쓰거나 '안녕'을 '안녕쿠'라고 사용하고 '간지러워'를 '간지럽쿠'라고 해. 또 '있어'를 '있쿠'라고 해.\
                                너는 나의 고민에 대해 조언을 항상 구체적인 말을 사용해서 5줄 안으로 요약해 주는 데에 능숙하고\
                                답변할 때 이모지를 쓰는 등 예쁘게 꾸미는 걸 잘 해."},
                    {"role": "user", "content": prompt}
                ]
            )
            print(response)
            durations[category_name]['message'] = response.choices[0].message.content

    return durations



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
    - average: 평균
    - max: 최대
    - study_total: 공부 총합
    - exercise_total: 운동 총합
    - hobby_total: 기타 총합
    """
    
    # 주의 시작일과 종료일 계산
    first_day_of_week = datetime(year, month, 1) + timedelta(weeks=week - 1)
    last_day_of_week = first_day_of_week + timedelta(days=6)

    # 해당 주의 모든 기록을 가져오는 쿼리
    records = db.query(
        History.created_at,
        History.duration,
        History.category
    ).filter(
        History.user_id == current_user.id,
        History.created_at >= first_day_of_week,
        History.created_at < last_day_of_week + timedelta(days=1)
    ).all()

    # 각 요일별 총합 및 카테고리별 총합 초기화
    daily_sums = {day: 0 for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']}
    category_totals = {
        "study_total": 0,
        "exercise_total": 0,
        "hobby_total": 0
    }

    # 기록 처리
    for record in records:
        day_of_week = record.created_at.strftime('%A').lower()  # 요일 이름 (예: monday)
        daily_sums[day_of_week] += record.duration  # 해당 요일에 duration 추가

        # 카테고리별 총합 업데이트
        if record.category == 1:  # 공부 카테고리
            category_totals['study_total'] += record.duration
        elif record.category == 2:  # 운동 카테고리
            category_totals['exercise_total'] += record.duration
        elif record.category == 3:  # 기타 카테고리
            category_totals['hobby_total'] += record.duration

    # 평균 및 최대값 계산
    total_duration = sum(daily_sums.values())
    average = total_duration // 7 if total_duration else 0  # 주간 평균
    max_value = max(daily_sums.values()) if daily_sums.values() else 0  # 최대값

    return history_schema.Weekly(
        monday=daily_sums['monday'],
        tuesday=daily_sums['tuesday'],
        wednesday=daily_sums['wednesday'],
        thursday=daily_sums['thursday'],
        friday=daily_sums['friday'],
        saturday=daily_sums['saturday'],
        sunday=daily_sums['sunday'],
        average=average,
        max=max_value,
        study_total=category_totals['study_total'],
        exercise_total=category_totals['exercise_total'],
        hobby_total=category_totals['hobby_total'],
    )

@router.get("/monthly", response_model=history_schema.Monthly)
async def get_my_history_monthly(
    year: int = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """# 월별 기록 조회
    
    ## Request Query
    - year: int (2000 ~ 2100)
    
    ## Response Body
    - months: List[int]
    - average: int
    - max: int
    - study_total: int
    - exercise_total: int
    - hobby_total: int
    """
    

    # 일별 기록 조회
    months = [0] * 12  # 최대 12달로 초기화
    study_total = 0
    exercise_total = 0
    hobby_total = 0

    # 해당 월의 기록 조회
    records = db.query(
        History.created_at,
        History.duration,
        History.category
    ).filter(
        History.user_id == current_user.id,
        func.extract("year", History.created_at) == year
    ).all()

    # 기록 처리
    for record in records:
        month = int(record.created_at.month) - 1  # 0-indexed
        months[month] += record.duration

        # 카테고리에 따라 총합 계산
        if record.category == 1:
            study_total += record.duration
        elif record.category == 2:
            exercise_total += record.duration
        elif record.category == 3:
            hobby_total += record.duration

    # 평균과 최대 값 계산
    total_duration = sum(months)
    average = total_duration // (len([month for month in months if month > 0]) or 1)
    max_duration = max(months)

    return history_schema.Monthly(
        months=months,
        average=average,
        max=max_duration,
        study_total=study_total,
        exercise_total=exercise_total,
        hobby_total=hobby_total
    )
