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
def create_history(
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