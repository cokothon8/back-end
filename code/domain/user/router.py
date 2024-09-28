from datetime import timedelta, datetime
import random
import re
import string
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config

from database import get_db
from domain.user import crud as user_crud
from domain.user import schema as user_schema
from werkzeug.security import check_password_hash

from models import User

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(config('REFRESH_TOKEN_EXPIRE_DAYS'))
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
oauth2_scheme_refresh = OAuth2PasswordBearer(tokenUrl="/users/token")

router = APIRouter(
    prefix="/users",
)



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Refresh 토큰의 만료 시간을 더 길게 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Refresh Token 검증 로직 추가 가능
        # 예: Refresh Token이 특정 리스트에 있는지 확인, 만료 시간 확인 등
    except JWTError:
        raise credentials_exception
    return {"username": username}


@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """# 로그인

    refresh_token 만료기간: 365days
    
    ## Request Body
    - username: str
    - password: str
    
    ## Response
    - access_token: str
    - token_type: str
    - refresh_token: str
    - username: str
    
    ## Response Code
    - 200: Success
    - 401: Unauthorized (Incorrect username or password)
    """
    # check user and password
    user = user_crud.get_user(db, form_data.username)
    if not user or not check_password_hash(user.password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
        refresh_token=refresh_token,
        username = form_data.username
    )
    

@router.post("/refresh-token", response_model=user_schema.RefreshedTokenResponse)
async def refresh_access_token(refresh_token: str = Depends(oauth2_scheme_refresh)):
    user_info = verify_refresh_token(refresh_token)
    username = user_info.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid refresh token",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    # 새로운 Refresh Token도 발급할 수 있습니다. 이 경우 기존 Refresh Token을 무효화해야 할 수도 있습니다.
    return user_schema.RefreshedTokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.post('/signup', response_model=user_schema.Token)
def signup(
    _user_create: user_schema.UserCreate,
    db: Session = Depends(get_db)
):
    """# 회원가입
    
    # Request Body
    - username: 닉네임
    - password: 패스워드
    
    # Response
    - access_token: str
    - token_type: str
    - refresh_token: str
    
    # Response Code
    - 200: Success
    - 409: Conflict (Username is already taken)
    """
    
    # check username
    user = user_crud.get_user(db, _user_create.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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