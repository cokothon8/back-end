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

def getUsername(db: Session, followeeName: str):
    db_user = db.query(User).filter(User.username == followeeName).first()

    return db_user

def isFollowed(db: Session,  followerId: int, followeeName: str):
    db_user = db.query(User).filter(User.username == followeeName).first()
    db_findfollow = db.query(FriendRelation).filter(FriendRelation.follower_id == followerId, FriendRelation.following_id == db_user.id).first()
    if db_findfollow:
        return True
    else:
        return False
    
def unfollowUser(db: Session, followerid: int, followeeName: str):
    
    db_user = db.query(User).filter(User.username == followeeName).first()
    
    follow_relation = db.query(FriendRelation)\
        .filter(FriendRelation.follower_id == followerid)\
        .filter(FriendRelation.following_id == db_user.id)\
        .first()
        
    db.delete(follow_relation)
    db.commit()