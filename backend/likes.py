from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user
from database import run_db
from models import Users, Post, Like

## Likes API

class LikeAPI:
    @staticmethod
    async def toggle_like(post_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if user already liked the post
        existing_like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
        
        if existing_like:
            # Unlike the post
            db.delete(existing_like)
            db.commit()
            return {"message": "Post unliked", "liked": False}
        else:
            # Like the post
            new_like = Like(
                user_id=user.id,
                post_id=post_id
            )
            db.add(new_like)
            db.commit()
            db.refresh(new_like)
            return {"message": "Post liked", "liked": True, "like": new_like}

    @staticmethod
    async def get_post_likes(post_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = db.query(Like).filter(Like.post_id == post_id).offset(skip).limit(limit).all()
        return likes

    @staticmethod
    async def get_post_likes_count(post_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes_count = db.query(Like).filter(Like.post_id == post_id).count()
        user_liked = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first() is not None
        
        return {
            "post_id": post_id,
            "likes_count": likes_count,
            "user_liked": user_liked
        }

    @staticmethod
    async def get_my_likes(skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        likes = db.query(Like).filter(Like.user_id == user.id).offset(skip).limit(limit).all()
        return likes

# Likes Router
likes_router = APIRouter(prefix="/likes", tags=["Likes"])
likes_router.post("/post/{post_id}")(LikeAPI.toggle_like)
likes_router.get("/post/{post_id}", response_model=List[LikeResponse])(LikeAPI.get_post_likes)
likes_router.get("/post/{post_id}/count")(LikeAPI.get_post_likes_count)
likes_router.get("/me", response_model=List[LikeResponse])(LikeAPI.get_my_likes)