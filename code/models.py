from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, ForeignKey, Table, func, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False, comment="닉네임")
    password = Column(String, nullable=False, comment="비밀번호")
    
    histories = relationship("History", back_populates="user")
    following = relationship("FriendRelation", foreign_keys="FriendRelation.follower_id", back_populates="follower")
    follower = relationship("FriendRelation", foreign_keys="FriendRelation.following_id", back_populates="following")


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="유저 아이디")
    category = Column(Integer, nullable=False, comment="카테고리") #1. 공부 2. 운동 3. 취미
    created_at = Column(DateTime, default=func.now(), comment="생성일")
    duration = Column(Integer, nullable=False, comment="시간 (초)")
    content = Column(Text, comment="내용")
    
    user = relationship("User", back_populates="histories")


class FriendRelation(Base):
    __tablename__ = "friend_relation"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="팔로워 아이디")
    following_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="팔로잉 아이디")
    
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="follower")
    