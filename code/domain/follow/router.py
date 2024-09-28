from datetime import timedelta, datetime
import random
import re
import string
from typing import Optional

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
    followee: follow_schema.followingUser,
    db: Session = Depends(get_db)
):
    """회원가입"""
    
    # check username
    user = follow_crud.get_user(db, _user_create.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken"
        )
    
    # create user
    user = user_crud.create_user(db, _user_create)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return user_schema.Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token
    )