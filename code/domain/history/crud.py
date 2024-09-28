from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import *
from domain.history.schema import *


def create_history(db: Session, history_create: HistoryCreate, current_user: User):
    db_history = History(
        user_id=current_user.id,
        category=history_create.category,
        duration=history_create.duration,
    )
    db.add(db_history)
    db.commit()

    return db_history


def get_my_history(db: Session, current_user: User):
    # 현재 달의 기록 조회
    return db.query(
        History.category,
        func.sum(History.duration).label("total_duration")
    ).filter(
        History.user_id == current_user.id,
        History.created_at >= datetime.now().replace(day=1),
    ).group_by(History.category).all()