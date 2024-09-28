from pydantic import BaseModel


class experience(BaseModel):
    study_total: int
    exercise_total: int
    hobby_total: int
    max_category: int