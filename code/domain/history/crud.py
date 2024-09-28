from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import *
from domain.history.schema import *
from sqlalchemy import *


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


def get_ranking(db: Session, user_id: int, category: int):
    ## 사용자가 팔로우하는 사람들의 이번 달 카테고리별 기록 합계를 구하고, 내림차순으로 정렬
    
    return db.query(
        User.username,
        func.coalesce(func.sum(History.duration), 0).label("total_duration")
    ).outerjoin(FriendRelation, User.id == FriendRelation.following_id) \
     .outerjoin(History, User.id == History.user_id) \
     .filter(
         (FriendRelation.follower_id == user_id) | (User.id == user_id),
         History.category == category,
         History.created_at >= datetime.now().replace(day=1),
     ).group_by(User.username) \
     .order_by(desc("total_duration")) \
     .all()
