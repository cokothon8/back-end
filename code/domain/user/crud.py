from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import *
from domain.user.schema import UserCreate


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   password=generate_password_hash(user_create.password, salt_length=8),
                   )
    db.add(db_user)
    db.commit()

    return db_user

    
    
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

