from datetime import date
from pydantic import BaseModel, validator
from typing import Optional, Dict


class HistoryCreate(BaseModel):
    category: int
    duration: int

class MyInfo(BaseModel):
    durations: Dict[int, int]  # 타입 어노테이션 추가

    class Config:
        orm_mode = True


class Ranking(BaseModel):
    username: str
    total_duration: int

    class Config:
        orm_mode = True