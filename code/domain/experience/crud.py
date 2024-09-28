from sqlalchemy.orm import Session
from models import *
from domain.experience.schema import experience



def searchCategoryDuration(db: Session,  currentUserId: int):
    db_experience = db.query(History).filter(History.user_id == currentUserId).all()
    return db_experience
  