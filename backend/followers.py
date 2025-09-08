from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user
from database import run_db
from models import Users, Follower

## Followers API

class FollowerAPI:
    @staticmethod
    async def follow_user(user_id: int, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if user exists
        user_to_follow = db.query(Users).filter(Users.id == user_id).first()
        if not user_to_follow:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is trying to follow themselves
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")
        
        # Check if already following
        existing_follow = db.query(Follower).filter(
            Follower.follower_id == current_user.id,
            Follower.following_id == user_id
        ).first()
        
        if existing_follow:
            raise HTTPException(status_code=400, detail="You are already following this user")
        
        # Create follow relationship
        new_follow = Follower(
            follower_id=current_user.id,
            following_id=user_id
        )
        db.add(new_follow)
        db.commit()
        db.refresh(new_follow)
        return {"message": f"You are now following {user_to_follow.username}", "follow": new_follow}

    @staticmethod
    async def unfollow_user(user_id: int, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if following relationship exists
        follow_relationship = db.query(Follower).filter(
            Follower.follower_id == current_user.id,
            Follower.following_id == user_id
        ).first()
        
        if not follow_relationship:
            raise HTTPException(status_code=404, detail="You are not following this user")
        
        db.delete(follow_relationship)
        db.commit()
        return {"message": "Successfully unfollowed user"}

    @staticmethod
    async def get_followers(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if user exists
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        followers = db.query(Follower).filter(Follower.following_id == user_id).offset(skip).limit(limit).all()
        return followers

    @staticmethod
    async def get_following(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if user exists
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        following = db.query(Follower).filter(Follower.follower_id == user_id).offset(skip).limit(limit).all()
        return following

    @staticmethod
    async def get_my_followers(skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        followers = db.query(Follower).filter(Follower.following_id == user.id).offset(skip).limit(limit).all()
        return followers

    @staticmethod
    async def get_my_following(skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        following = db.query(Follower).filter(Follower.follower_id == user.id).offset(skip).limit(limit).all()
        return following

    @staticmethod
    async def get_follow_stats(user_id: int, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if user exists
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        followers_count = db.query(Follower).filter(Follower.following_id == user_id).count()
        following_count = db.query(Follower).filter(Follower.follower_id == user_id).count()
        
        # Check if current user is following this user
        is_following = db.query(Follower).filter(
            Follower.follower_id == current_user.id,
            Follower.following_id == user_id
        ).first() is not None
        
        return {
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following
        }

# Followers Router
followers_router = APIRouter(prefix="/follow", tags=["Followers"])
followers_router.post("/{user_id}")(FollowerAPI.follow_user)
followers_router.delete("/{user_id}")(FollowerAPI.unfollow_user)
followers_router.get("/followers/{user_id}", response_model=List[FollowerResponse])(FollowerAPI.get_followers)
followers_router.get("/following/{user_id}", response_model=List[FollowerResponse])(FollowerAPI.get_following)
followers_router.get("/my-followers", response_model=List[FollowerResponse])(FollowerAPI.get_my_followers)
followers_router.get("/my-following", response_model=List[FollowerResponse])(FollowerAPI.get_my_following)
followers_router.get("/stats/{user_id}")(FollowerAPI.get_follow_stats)