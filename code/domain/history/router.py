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