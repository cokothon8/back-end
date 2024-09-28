from datetime import date
from pydantic import BaseModel, validator
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    username: str


class RefreshedTokenResponse(BaseModel):
    access_token: str
    token_type: str
