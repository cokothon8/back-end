from domain.user.router import get_current_user
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.experience import crud as experience_crud
from domain.experience import schema as experience_schema

from models import *

router = APIRouter(
    prefix="/history/experience",
)

@router.get('', response_model=experience_schema.experience)
async def searchDuration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 경험치 조회 엔드포인트
        
    ## Response
    - study_total: int
    - exercise_total: int
    - hobby_total: int
    
    ##Response Code
    - 200: Success
    """
        
    # return duration
    
    categoryDurationList = experience_crud.searchCategoryDuration(db, current_user.id)
    studydurationlist = list()
    exercisedurationlist = list()
    hobbydurationlist = list()
    for i in categoryDurationList:
        if i.category == 1: # 공부
            studydurationlist.append(i.duration)
        elif i.category == 2: # 운동
            exercisedurationlist.append(i.duration)
        elif i.category == 3: # 취미
            hobbydurationlist.append(i.duration)
    study_total = sum(studydurationlist)
    exercise_total = sum(exercisedurationlist)
    hobby_total = sum(hobbydurationlist)
    max_value = max(study_total, exercise_total, hobby_total)
    max_category = 0
    if max_value == study_total:
        max_category = 1
    elif max_value == exercise_total:
        max_category = 2
    elif max_value == hobby_total:
        max_category = 3
        
    return experience_schema.experience(
        study_total = study_total,
        exercise_total =  exercise_total,
        hobby_total = hobby_total,
        max_category = max_category
    )