from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import *
from domain.follow.schema import FollowingUser


def followUser(db: Session, follow_user: FollowingUser):
    db_friendrelation = FriendRelation(following=follow_user.username)
    db.add(db_friendrelation)
    db.commit()

    return db_friendrelation
