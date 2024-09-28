from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import *
from domain.follow.schema import followingUser


def followUser(db: Session,  follower_id: int, following_name: str):
    db_following_user = db.query(User).filter(User.username == following_name).first()
    db_friendrelation = FriendRelation(
        follower_id = follower_id,
        following_id = db_following_user.id
    )
    db.add(db_friendrelation)
    db.commit()

    return db_friendrelation
