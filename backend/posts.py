from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user
from database import run_db
from models import Users, Post, Comment, Like

## Posts API

class PostAPI:
    @staticmethod
    async def create_post(post_data: PostCreate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        new_post = Post(
            content=post_data.content,
            user_id=user.id
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    @staticmethod
    async def get_all_posts(skip: int = 0, limit: int = 20, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        posts = db.query(Post).offset(skip).limit(limit).all()
        return posts

    @staticmethod
    async def get_post(post_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    @staticmethod
    async def get_user_posts(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        posts = db.query(Post).filter(Post.user_id == user_id).offset(skip).limit(limit).all()
        return posts

    @staticmethod
    async def get_my_posts(skip: int = 0, limit: int = 20, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        posts = db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()
        return posts

    @staticmethod
    async def update_post(post_id: int, post_data: PostCreate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found or you don't have permission")
        
        post.content = post_data.content
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    async def delete_post(post_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found or you don't have permission")
        
        db.delete(post)
        db.commit()
        return {"message": "Post deleted successfully"}

# Posts Router
posts_router = APIRouter(prefix="/posts", tags=["Posts"])
posts_router.post("/", response_model=PostResponse)(PostAPI.create_post)
posts_router.get("/", response_model=List[PostResponse])(PostAPI.get_all_posts)
posts_router.get("/me", response_model=List[PostResponse])(PostAPI.get_my_posts)
posts_router.get("/{post_id}", response_model=PostResponse)(PostAPI.get_post)
posts_router.get("/user/{user_id}", response_model=List[PostResponse])(PostAPI.get_user_posts)
posts_router.put("/{post_id}", response_model=PostResponse)(PostAPI.update_post)
posts_router.delete("/{post_id}")(PostAPI.delete_post)