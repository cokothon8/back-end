from datetime import date
from pydantic import BaseModel, validator
from typing import Optional


class followingUser(BaseModel):
    username: str
