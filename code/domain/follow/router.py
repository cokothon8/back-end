from domain.user.router import get_current_user
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.follow import crud as follow_crud
from domain.follow import schema as follow_schema

from models import FriendRelation

router = APIRouter(
    prefix="/follow",
)

@router.post('/{followee}', response_model=follow_schema.followingUser)
async def follow(
    followee: str,
    current_user: FriendRelation = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 팔로우 엔드포인트
    
    
    ## Path Parameter
    - followee: str 
    
    ## Response
    - username: str
    
    ##Response Code
    - 200: Success
    - 400: Bad Request  (Cannot follow myself)
    - 404: Not Found    (Usename is unavailable)
    - 409: Bad Request  (Already Followed) 
    """
    
    # check username
    user = follow_crud.getUsername(db, followee)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username is unavailable."
        )
    elif user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow myself"
        )
        
    if follow_crud.isFollowed(db, current_user.id, followee):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already Followed."
        )
        
        
    # follow user
    
    follow_crud.followUser(db, current_user.id, followee)
    
    return follow_schema.followingUser(
        username=followee
    )
    
    
    
@router.delete('/{followee}', response_model=follow_schema.followingUser)
async def follow(
    followee: str,
    current_user: FriendRelation = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 언팔로우 엔드포인트
    
    
    ## Path Parameter
    - followee: str 
    
    ## Response
    - username: str
    
    ##Response Code
    - 200: Success
    - 400: Bad Request  (Cannot unfollow myself)
    - 404: Not Found    (Usename is unavailable)
    - 409: Bad Request  (Already Unfollowed) 
    """
    
    # check username
    user = follow_crud.getUsername(db, followee)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username is unavailable."
        )
    
    elif user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unfollow myself"
        )
        
        
    if not follow_crud.isFollowed(db, current_user.id, followee):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already Unfollowed."
        )
        
        
    # follow user
    
    follow_crud.unfollowUser(db, current_user.id, followee)
    
    return follow_schema.followingUser(
        username=followee
    )