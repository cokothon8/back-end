from datetime import timedelta, datetime
import random
import re
import string
from typing import Optional
from domain.user.router import get_current_user
from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config

from database import get_db
from domain.follow import crud as follow_crud
from domain.follow import schema as follow_schema
from werkzeug.security import check_password_hash

from models import FriendRelation

router = APIRouter(
    prefix="/follow",
)

@router.post('/follow/{follower}', response_model=follow_schema.followingUser)
async def follow(
    follower: follow_schema.followingUser,
    current_user: FriendRelation = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 팔로우하기 엔드포인트
    - follower : 팔로우당할 사람
    - current_user : 현재 사용자
    """
    
    # check username
    user = follow_crud.followUser(db, current_user.id, follower.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is unavailable."
        )
    
    # follow user
    
    return follow_crud.followUser(db, follower, current_user)