from datetime import date
from pydantic import BaseModel, validator
from typing import Optional


class HistoryCreate(BaseModel):
    category: int
    duration: int

