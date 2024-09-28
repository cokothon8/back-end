from datetime import date
from pydantic import BaseModel, validator
from typing import Optional, Dict


class HistoryCreate(BaseModel):
    category: int
    duration: int
    content: Optional[str] = None

class MyInfo(BaseModel):
    durations: Dict[int, int]  # 타입 어노테이션 추가

    class Config:
        orm_mode = True


class Ranking(BaseModel):
    username: str
    total_duration: int

    class Config:
        orm_mode = True
        

class Weekly(BaseModel):
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    average: int
    max: int
    study_total: int
    exercise_total: int
    etc_total: int


class Monthly(BaseModel):
    days: list[int]
    average: int
    max: int
    study_total: int
    exercise_total: int
    etc_total: int
