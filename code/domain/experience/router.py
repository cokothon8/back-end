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

@router.get('/{category}', response_model=experience_schema.experience)
async def searchDuration(
    category: int, #1: 공부, 2: 운동, 3: 취미
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 경험치 조회 엔드포인트
    
    
    ## Path Parameter
    - category: int
    
    ## Response
    - category: int (1. 공부, 2. 운동, 3. 취미)
    - duration: int (초)
    
    ##Response Code
    - 200: Success
    - 400: Bad Request  (Category is unavailable.)
    """
    
    # check category
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is unavailable."
        )
        
    # return duration
    
    categoryDurationList = experience_crud.searchCategoryDuration(db, current_user.id, category)
    durationlist = list()
    for i in categoryDurationList:
        durationlist.append(i.duration)
    duration = sum(durationlist)
    return experience_schema.experience(
        category = category,
        duration = duration
    )