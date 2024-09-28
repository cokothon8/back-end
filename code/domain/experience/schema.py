from pydantic import BaseModel


class experience(BaseModel):
    category: int
    duration: int